#  MindMesh

**MindMesh** is a community-driven platform where developers can share ideas, create discussions, and grow knowledge together.

---

##  Features

* 👤 User Authentication (Sign up / Sign in)
* 🔐 Admin Panel with secure access
* 📝 Create, edit, and delete posts
* 💬 Comment system
* 👍 Like / 👎 Dislike functionality
* 🧑‍💻 Guest browsing mode
* 🏷️ Category-based posts
* 🎨 Clean and responsive UI

---

##  Tech Stack

* **Backend:** Flask (Python)
* **Database:** MySQL
* **Frontend:** HTML, CSS, JavaScript
* **Authentication:** Password hashing (Werkzeug)
* **Environment Management:** dotenv

---

## Project Structure

```
MindMesh/
│
├── app.py
├── schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
│
├── static/
│   ├── style.css
│   └── main.js
│
├── templates/
│   ├── index.html
│   ├── home.html
│   ├── sign_in.html
│   ├── sign_up.html
│   ├── admin_login.html
│   ├── post_create.html
│   ├── post_detail.html
│   ├── edit_post.html
│   ├── edit_comment.html
│   └── guest.html
```

---

##  Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/keshavai2003-hash/MindMesh.git
cd MindMesh
```

---

### 2. Install dependencies

```
pip install -r requirements.txt
```

---

### 3. Setup Database

1. Create a MySQL database (e.g. `itt`)
2. Import the schema:

```
SOURCE schema.sql;
```

---

### 4. Configure Environment Variables

Create a `.env` file:

```
SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=itt
DEBUG=True
```

---

### 5. Run the application

```
python app.py
```

---

##  Future Improvements

* 🔍 Search & filter posts
* 👤 User profile pages
* 🖼️ Image uploads
* 📄 Pagination
* 🌐 Deployment (Render / Railway)

---

##  Contributing

Feel free to fork this repo and submit pull requests.

---

##  Author

**Keshav**
Built by keshav

---

##  Support

If you like this project, give it a ⭐ on GitHub!
