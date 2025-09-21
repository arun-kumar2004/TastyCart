# 🍴 TastyCart - Django Food Delivery Web App

✨ **TastyCart** is a full-featured **Food Delivery Web Application** built with **Django**.  
It allows customers to browse the menu, add items to the cart, place orders, track delivery, and make secure payments.

---

## 🚀 Features

- 👤 **User Authentication** (Signup/Login/Logout)
- 🛒 **Cart Management**
- 📦 **Order Placement & Tracking**
- 💳 **Online Payments**
- 📢 **Notifications**
- ⭐ **Reviews & Ratings**
- 👨‍💼 **Admin Panel for Restaurant Management**
- 📱 **Responsive Design**

---

## 🛠️ Tech Stack

- **Backend:** Django, Python  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **Database:** SQLite (can be switched to MySQL/PostgreSQL)  
- **Payments:** Stripe / Razorpay (integration ready)  

---

## 📂 Project Structure

TastyCart/
│── adminpanel/ # Custom admin features
│── cart/ # Cart management
│── contact/ # Contact page
│── core/ # Core settings
│── delivery/ # Delivery tracking
│── menu/ # Menu management
│── notifications/ # Alerts & notifications
│── orders/ # Orders module
│── payments/ # Payment gateway integration
│── reviews/ # Reviews & ratings
│── users/ # User accounts
│── media/ # Uploaded media (ignored in repo)
│── manage.py # Django project manager

yaml
Copy code

---

## ⚡ Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/arun-kumar2004/TastyCart.git
   cd TastyCart
Create Virtual Environment

bash
Copy code
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Linux/Mac
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Setup Environment Variables

Create a .env file

Add your SECRET_KEY, DATABASE_URL, EMAIL_HOST, and API keys.

Run Migrations

bash
Copy code
python manage.py migrate
Run Development Server

bash
Copy code
python manage.py runserver
🎯 Future Enhancements
✅ Mobile app version (React Native / Flutter)

✅ Real-time order tracking with WebSockets

✅ Advanced analytics dashboard for restaurants

🤝 Contributing
Pull requests are welcome!
For major changes, please open an issue first to discuss what you would like to change.

📜 License
This project is licensed under the MIT License.

👨‍💻 Author
Arun Kumar
🔗 GitHub
🔗 LinkedIn
