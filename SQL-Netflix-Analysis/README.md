# 🎬 Netflix SQL Analysis (PostgreSQL)

This project showcases advanced SQL queries and analytical techniques applied to a Netflix dataset using **PostgreSQL**.  
It demonstrates data analysis, aggregation, text parsing, and date manipulation to extract valuable business insights.

---

## 📘 Dataset Information

**Table name:** `netflix`  
**Columns:**
- `show_id` – Unique ID of the show  
- `type` – Movie or TV Show  
- `title` – Title of the content  
- `director` – Director name  
- `casts` – List of main actors  
- `country` – Country of production  
- `date_added` – Date the title was added to Netflix  
- `release_year` – Year of release  
- `rating` – Content rating (e.g., PG, TV-MA)  
- `duration` – Duration (minutes for movies, seasons for shows)  
- `listed_in` – Genre/category  
- `description` – Short description  

---

## 🎯 Objectives
This project aims to:
- Perform **in-depth data analysis** using SQL.
- Explore **content trends**, **genre diversity**, and **global distribution**.

---

## 🧠 Key SQL Queries & Insights

### 1️⃣ Top 10 Directors by Number of Titles
Finds the most frequent directors on Netflix.

### 2️⃣ Country-Wise Content in the Last 5 Years
Analyzes which countries have released the most content recently.

### 3️⃣ Average Movie Duration by Rating
Compares content length across rating categories.

### 4️⃣ Most Common Genre Combinations
Identifies popular genre mixes (e.g., “Dramas, International Movies”).

### 5️⃣ Movies with Same Title Released in Different Years
Finds remakes or repeated titles.

### 6️⃣ Directors with the Most Diverse Genres
Shows directors who worked across multiple genres.

### 7️⃣ Top 5 Countries by Average Movie Duration
Finds which countries produce longer or shorter movies on average.

### 8️⃣ Monthly Content Additions in the Last 2 Years
Tracks Netflix’s recent content addition trends.

### 9️⃣ Actors Appearing in Both Movies and TV Shows
Highlights versatile actors who worked across formats.

### 🔟 Trending Genres in India (Last 5 Years)
Identifies currently popular genres in India.

---

## 🧾 Example Insight
> “India and the United States dominate Netflix’s content catalog, with **‘Dramas’** and **‘Comedies’** being the most common genres.  
> Directors like *Raul Campos* and *Jan Suter* consistently appear among the top creators.”

---

## ⚙️ Tools & Technologies
- **Database:** PostgreSQL  
- **Language:** SQL  
- **Platform:** pgAdmin 
- **Data Source:** Netflix Titles Dataset (Kaggle)

