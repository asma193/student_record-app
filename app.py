import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "students.db"

# ---------- Database Functions ----------

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            grade TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_student(name, age, grade):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))
    conn.commit()
    conn.close()

def view_students():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def update_student(student_id, name, age, grade):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE students SET name=?, age=?, grade=? WHERE id=?", (name, age, grade, student_id))
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

def search_students(query):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students WHERE name LIKE ?", conn, params=(f"%{query}%",))
    conn.close()
    return df

# ---------- Streamlit App ----------

st.set_page_config(page_title="Student Management System", page_icon="🎓", layout="centered")

st.title("🎓 Student Record Management System")
st.caption("Built using Streamlit + SQLite (Waterfall Model Example)")

init_db()  # ensure DB exists

menu = ["Add Student", "View All", "Update Student", "Delete Student", "Search Student"]
choice = st.sidebar.selectbox("Select Operation", menu)

# ---------- Add ----------
if choice == "Add Student":
    st.subheader("➕ Add New Student")
    name = st.text_input("Enter Student Name")
    age = st.number_input("Enter Age", min_value=1, max_value=100, step=1)
    grade = st.text_input("Enter Grade (e.g. 10th, 12th, etc.)")

    if st.button("Add Student"):
        if name.strip() == "" or grade.strip() == "":
            st.warning("Please enter valid details.")
        else:
            add_student(name, age, grade)
            st.success(f"✅ Student '{name}' added successfully!")

# ---------- View ----------
elif choice == "View All":
    st.subheader("📋 All Students")
    df = view_students()
    if df.empty:
        st.info("No students found.")
    else:
        st.dataframe(df)

# ---------- Update ----------
elif choice == "Update Student":
    st.subheader("✏️ Update Student Record")
    df = view_students()
    if df.empty:
        st.info("No students to update.")
    else:
        st.dataframe(df)
        student_ids = df["id"].tolist()
        selected_id = st.selectbox("Select Student ID", student_ids)
        selected_student = df[df["id"] == selected_id].iloc[0]

        new_name = st.text_input("Name", selected_student["name"])
        new_age = st.number_input("Age", value=int(selected_student["age"]), min_value=1, max_value=100)
        new_grade = st.text_input("Grade", selected_student["grade"])

        if st.button("Update"):
            update_student(selected_id, new_name, new_age, new_grade)
            st.success(f"✅ Student ID {selected_id} updated successfully!")

# ---------- Delete ----------
elif choice == "Delete Student":
    st.subheader("🗑️ Delete Student Record")
    df = view_students()
    if df.empty:
        st.info("No students to delete.")
    else:
        st.dataframe(df)
        student_ids = df["id"].tolist()
        selected_id = st.selectbox("Select Student ID to delete", student_ids)
        if st.button("Delete"):
            delete_student(selected_id)
            st.warning(f"⚠️ Student ID {selected_id} deleted successfully!")

# ---------- Search ----------
elif choice == "Search Student":
    st.subheader("🔍 Search Student by Name")
    query = st.text_input("Enter part of the student's name")
    if st.button("Search"):
        if query.strip() == "":
            st.warning("Please enter a name to search.")
        else:
            results = search_students(query)
            if results.empty:
                st.info("No matching students found.")
            else:
                st.dataframe(results)
