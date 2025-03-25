# 📦 Reorder Point (ROP) Calculator

## 🧭 Overview
This tool helps inventory planners calculate Reorder Points (ROP) using historical transaction data and bootstrap simulation. It's especially useful for **lumpy** or **intermittent** demand patterns where traditional statistical methods may fail.

## 🚀 How to Use

### 1. Upload Your Excel File
- The file **must contain** the following columns:
  - `calendar_date`
  - `item_number`
  - `quantity`
- Optionally, include `branch_number` if you're analyzing data by branch.
- File size must be **under 200MB** (Streamlit's upload limit).

### 2. Configure Parameters (in the sidebar)
- Lead time in working days
- Working days per week
- Bootstrap sample size
- ABC service levels

### 3. Click **"Run"** (or the app runs automatically after upload)
- Results will be shown in the app and available to download as an Excel file with two sheets:
  - `ROP Results`: items that qualify for ROP calculation
  - `Needs Review`: items that don’t meet minimum data requirements

---

## 🧠 Core Logic

### ✅ Qualified Items
An item is considered **"Qualified"** for ROP calculation if:
- Average monthly demand is **≥ 0.5 units**
- Total number of transactions (distinct days with sales) is **≥ 10**

Items that don't meet these criteria are flagged for **manual review** in the `Needs Review` sheet.

---

### 🔢 ABC Classification
Among qualified items:
- Items are sorted by total quantity sold.
- Classification:
  - **A**: Top 80% of cumulative volume
  - **B**: Next 15%
  - **C**: Remaining 5%

### 🎯 Service Levels (default settings)
- A items: 95%
- B items: 85%
- C items: 75%

You can adjust these in the sidebar.

---

### 📈 ROP Calculation via Bootstrap
- Weekly demand is resampled from historical data.
- For each sample, demand during lead time is simulated.
- The final ROP is the **percentile** based on your service level.
- If demand is lumpy and bootstrap result is unusually low, a **mode override** is applied to avoid understocking.

---

## ⚠️ Performance Notice
Depending on the number of items and data history, this app may take **up to several minutes** to run — especially on large files or less powerful machines.

---

## 👨‍💻 Author
Yi Han | Made with 💪 and 🍵

---

## 📜 License
MIT License
