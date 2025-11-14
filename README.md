# Auctions Web Application

Auctions is a full-featured online auction platform built with Django. It allows users to create listings, place bids, leave comments, manage a watchlist, and browse by category. The application demonstrates advanced use of Django models, views, forms, and template rendering, along with real-time bid validation and user-specific interactions.

## Key Features

The application includes several sophisticated features that go beyond a basic CRUD web app:

- Real-time bidding with validation to ensure that each bid is greater than the current highest bid and not below the starting price.
- Dynamic watchlist management, allowing users to add or remove listings and view their personalized watchlist.
- Conditional page rendering based on user authentication and ownership, including the ability for listing creators to close auctions and declare winners.
- Commenting system tied to individual listings with proper relational database management, showing comments in reverse chronological order.
- Category management for listings, including filtering listings by category. 

These features combine to create an interactive, user-centric auction platform that handles complex logic in the backend while remaining intuitive for end users.

## Installation and Setup

Follow these steps to run the application locally.

1. **Clone the repository**
    ```bash
    git clone <your-repo-link>
    cd auctions
    ```

2. **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate   # macOS/Linux
    venv\Scripts\activate      # Windows
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply database migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Create an administrative user (optional)**
    ```bash
    python manage.py createsuperuser
    ```

6. **Start the development server**
    ```bash
    python manage.py runserver
    ```

7. **Open a browser and visit**
    ```
    http://127.0.0.1:8000
    ```

You can now register new accounts, create listings, place bids, comment, and explore categories.

## Summary

This application showcases advanced backend logic, dynamic user interactions, and relational data management in a Django environment. It can serve as a foundation for more complex e-commerce or auction-based web platforms and demonstrates professional-level Django development skills.
