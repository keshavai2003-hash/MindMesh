# MindMesh

**MindMesh** is a community-driven platform where developers can share ideas, create discussions, and grow knowledge together.

---

##  Features

* 👤 User Authentication (Sign up / Sign in)
* 🔐 Admin Panel with special access
* 📝 Create, edit, and delete posts
* 💬 Comment system on posts
* 👍 Like / 👎 Dislike functionality
* 🧑‍💻 Guest access (browse without login)
* 🏷️ Category-based posts
* 🎨 Clean and responsive UI

---

##  Tech Stack

* **Backend:** Flask (Python)
* **Database:** MySQL
* **Frontend:** HTML, CSS, JavaScript
* **Authentication:** Secure password hashing
* **Environment Management:** dotenv

---

## Project Structure

```
MindMesh/
│
├── app.py
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

1. Clone the repository:

```
git clone https://github.com/keshavai2003-hash/MindMesh.git
```

2. Navigate to the project:

```
cd MindMesh
```

3. Create a virtual environment and activate it

4. Install dependencies:

```
pip install -r requirements.txt
```

5. Create a `.env` file based on `.env.example`:

```
SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=itt
DEBUG=True
```

6. Run the app:

```
python app.py
```

---

##  Future Improvements

* 🔍 Search and filter posts
* 🖼️ Image upload support
* 📄 Pagination for posts
* 👤 User profile pages
* 🌐 Deployment (Render / Railway)

---

##  Contributing

Contributions are welcome! Feel free to fork the repo and submit a pull request.

---

##  Author

**Keshav**
Build by using Flask

---

## ⭐ Show your support

If you like this project, give it a ⭐ on GitHub!
