"""
Management command: cleanup_storage
Deletes the oldest waste report images from Supabase S3 storage
when total storage usage exceeds 50MB.

Run via: python manage.py cleanup_storage
Or call via Vercel cron: GET /api/v1/admin/cleanup-storage/
"""
import os
import boto3
from botocore.client import Config
from django.core.management.base import BaseCommand
from waste.models import Report

# 50 MB limit in bytes
STORAGE_LIMIT_BYTES = 50 * 1024 * 1024


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('SUPABASE_S3_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('SUPABASE_S3_SECRET_ACCESS_KEY'),
        endpoint_url=os.environ.get('SUPABASE_S3_ENDPOINT_URL'),
        region_name=os.environ.get('SUPABASE_S3_REGION_NAME', 'eu-west-1'),
        config=Config(signature_version='s3v4'),
    )


def get_bucket_name():
    return os.environ.get('SUPABASE_S3_BUCKET_NAME', 'waste-images')


def get_total_bucket_size(s3, bucket):
    """Returns total size in bytes of all objects in the bucket."""
    total = 0
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get('Contents', []):
            total += obj['Size']
    return total


def run_cleanup(dry_run=False, verbose=True):
    """
    Core cleanup logic. Deletes the oldest waste report images
    until total size is below 50MB.

    Returns: dict with stats
    """
    s3 = get_s3_client()
    bucket = get_bucket_name()

    total_size = get_total_bucket_size(s3, bucket)
    total_mb = total_size / (1024 * 1024)

    stats = {
        'initial_size_mb': round(total_mb, 2),
        'limit_mb': 50,
        'deleted_count': 0,
        'freed_mb': 0,
        'needed_cleanup': total_size > STORAGE_LIMIT_BYTES,
    }

    if verbose:
        print(f"Current storage: {total_mb:.2f} MB / 50 MB limit")

    if total_size <= STORAGE_LIMIT_BYTES:
        if verbose:
            print("✅ Storage is within limit. No cleanup needed.")
        return stats

    if verbose:
        print(f"⚠️  Storage exceeds 50MB. Starting cleanup...")

    # Get oldest reports with images, ordered by created_at (oldest first)
    reports_with_images = Report.objects.exclude(
        image=''
    ).exclude(
        image=None
    ).order_by('created_at')

    freed = 0
    deleted_count = 0

    for report in reports_with_images:
        if total_size - freed <= STORAGE_LIMIT_BYTES:
            break  # We're back under the limit

        image_name = str(report.image)  # e.g. "waste_image/abc.jpg"
        if not image_name:
            continue

        try:
            # Get object size before deleting
            head = s3.head_object(Bucket=bucket, Key=image_name)
            obj_size = head['ContentLength']

            if not dry_run:
                # Delete from S3
                s3.delete_object(Bucket=bucket, Key=image_name)
                # Clear the image field on the report (keep the report record)
                report.image = None
                report.save(update_fields=['image'])

            freed += obj_size
            deleted_count += 1

            if verbose:
                freed_mb = freed / (1024 * 1024)
                print(f"  {'[DRY RUN] ' if dry_run else ''}Deleted: {image_name} ({obj_size/1024:.1f} KB) — freed {freed_mb:.2f} MB so far")

        except Exception as e:
            if verbose:
                print(f"  ⚠️ Could not delete {image_name}: {e}")
            continue

    stats['deleted_count'] = deleted_count
    stats['freed_mb'] = round(freed / (1024 * 1024), 2)
    stats['final_size_mb'] = round((total_size - freed) / (1024 * 1024), 2)

    if verbose:
        print(f"\n✅ Cleanup complete: deleted {deleted_count} files, freed {stats['freed_mb']} MB")

    return stats


class Command(BaseCommand):
    help = 'Delete oldest waste images from Supabase when storage exceeds 50MB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE — nothing will be deleted'))
        stats = run_cleanup(dry_run=dry_run, verbose=True)
        if stats['needed_cleanup']:
            self.stdout.write(self.style.SUCCESS(
                f"Freed {stats['freed_mb']} MB by deleting {stats['deleted_count']} files."
            ))
        else:
            self.stdout.write(self.style.SUCCESS('No cleanup needed.'))
