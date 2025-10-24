# 🛍️ Full-Stack E-Commerce Website (Django Online Store)

**Version:** Build 1.0.9 (Early Development Stage)  
**Timeline:** March 2025 – June 2025  
**Status:** 🚧 In Development  

A complete **full-stack e-commerce platform** built from scratch using **Django (Python)** for the backend and **HTML5, CSS3, JavaScript, and Bootstrap** for the frontend.  
This project demonstrates **end-to-end web application development** from authentication and product management to analytics and checkout — built with scalability and maintainability in mind.

---

![Homepage Screenshot](https://github.com/Mohd-Amir-ai/Hivefusion-lab-website-/blob/main/Demo-01.png?raw=true)


## 🚀 Features

### 🧠 Backend Development
- Developed with **Django** using the **MVT architecture**.
- Full **user authentication** system — login, logout, signup, password management.
- Complete **product management** (CRUD operations for admin panel).
- Dynamic **cart and checkout** system with real-time updates.

### 🗄️ Database Integration
- **SQLite** database integration for products, users, and order data.
- Designed for smooth CRUD operations and data reliability.

### ⚙️ Custom Middleware (Analytics Engine)
- Custom **Django middleware** to track:
  - User sessions and active time
  - Page visits and click events
  - Traffic sources and behavior flow  
- Enables actionable analytics to improve engagement and sales.

### 🎨 Frontend Design
- **Responsive UI** using HTML5, CSS3, JavaScript, and Bootstrap.
- Optimized for all screen sizes and browsers.
- Focused on a clean and professional shopping experience.

---

## 🧰 Tech Stack

| Category | Technologies |
|-----------|---------------|
| **Backend** | Python, Django |
| **Database** | SQLite |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Version Control** | Git & GitHub |

---

## ⚡ Setup & Installation

To run this project locally:

```bash
# 1️⃣ Clone the repository
git clone https://github.com/Mohd-Amir-ai/Hivefusion-lab-website-.git
cd <repo-name>

# 2️⃣ Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run migrations
python manage.py migrate

# 5️⃣ Start the development server
python manage.py runserver
