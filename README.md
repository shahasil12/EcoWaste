
# EcoWaste :recycle: – Smart Waste Management Portal

A modern Django web application for citizens and companies to **find recycle bins, report waste, and track environmental impact**.  
Includes real-time bin locations (map), dynamic statistics, smart reporting (with nearest-bin fee waiver), and an interactive FAQ assistant.

## Features

- **Bin Location Map** – Visualize nearby recycle bins on an interactive map (Leaflet).
- **"Find Bins Near Me"** – Instantly jump to the map to locate bins in your area.
- **Report Waste** – Pin your waste location, see the nearest bin, and get a fee waiver for dropping waste at the optimal spot.
- **Smart Fee Logic** – Users who select the closest bin for disposal pay zero fee (securely checked).
- **Nearby Bins List** – See all bins sorted and styled by status and accepted waste types.
- **Company Portal** – Separate access for companies via a dedicated login.
- **Real-Time Statistics** – Dashboard showing total bins, full bins, available bins.
- **EcoWaste Assistant** – Friendly FAQ bot for instant help.
- **Mobile Friendly** – Responsive Bootstrap UI.

## Demo

![EcoWaste Preview a real screenshot if you have one!)*

## Getting Started

### Prerequisites

- Python 3.9+ (recommended)
- Django 3.2+
- Node.js (optional, for SCSS/CSS processing)
- A modern web browser

### Setup Instructions

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/ecowaste.git
    cd ecowaste
    ```

2. **Install Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Make migrations and migrate:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4. **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

5. **Run the server:**

    ```bash
    python manage.py runserver
    ```

6. **Access the app:**

    - Visit [http://localhost:8000/](http://localhost:8000/) in your browser.
    - Login at `/admin` and add some `Bin` locations to get started.

## Usage

- **Citizen/User:**  
  - Click "Find Bins Near Me" to jump to the map.
  - Use the map/list to find and select a nearby bin.
  - Report waste by pinning your location; if you choose the nearest bin, the fee is waived.
- **Company:**  
  - Click "Company Portal" to redirect to company login.
- **Admin:**  
  - Use the Django admin interface to add or update bin details.

## Customization

- Edit `templates/` for branding and content.
- Add/modify bins in the Django admin.
- The FAQ bot can be found/configured in `js/script.js`.
- Adjust fee logic in `views.py` as required.

## Technologies

- Django
- Bootstrap 5
- Leaflet.js (for map)
- FontAwesome & Bootstrap Icons

## Folder Structure

```
ecowaste/
  ├─ manage.py
  ├─ ecowaste/           # Django project folder
  │    ├─ settings.py
  ├─ bins/               # Your main app folder (or adjust accordingly)
  │    ├─ models.py
  │    ├─ views.py
  │    ├─ templates/
  │    ├─ static/
  ├─ static/
  │   ├─ js/
  │   │   └─ script.js
  └─ README.md
```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE) *(or your preferred License)*

## Credits

- Problem/solution, guidance and assistant logic by [Perplexity AI](https://www.perplexity.ai/)
- Map data © [OpenStreetMap](https://www.openstreetmap.org/)

**Questions?**  
Open an issue or ask in the assistant widget/chat.

**Happy cleaning with EcoWaste! :seedling::recycle:**

**You can name your app and customize further as you like.  
Add/remove sections for any API keys or deployment notes you have!**

If you need the content in a .md file format or extra sections (deployment, environment variables, etc.), let me know!
