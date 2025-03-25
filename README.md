📦 Reorder Point (ROP) Calculator – Overview
This tool helps inventory planners calculate Reorder Points (ROP) for items using bootstrap simulation, particularly useful when dealing with lumpy or intermittent demand.

🎯 Purpose
Designed to assist in setting ROPs using historical demand data provided in Excel, this app:

Calculates ROPs per item

Classifies items using ABC analysis

Flags items that lack sufficient demand data and require human review

🧠 Core Logic
✅ Qualified Items
An item is considered "Qualified" for ROP calculation if:

Average monthly demand is ≥ 0.5 units

Transaction count (distinct days with sales) is ≥ 10

These criteria ensure we don’t blindly calculate reorder points for items that barely move or only sold a couple times by chance.

❌ Human Review Needed
Items that don’t meet either criterion are tagged as “Human check needed”. Why?

Because trying to generate a reorder point for extremely low-demand or one-off items can lead to:

Overordering dead stock

False confidence in simulation-based ROPs

Misuse of working capital

Instead, these items are flagged for manual consideration (e.g. phase-out, special order only, or seasonal handling).

📊 How It Works
Upload a file with calendar_date, item_number, and quantity

Optionally provide branch_number

Adjust sliders for:

Lead time

Working days per week

Service levels by ABC class

Click Run to simulate ROPs using bootstrap for qualified items

Download the result:

Sheet 1: ROP results for qualified items

Sheet 2: Items requiring human review
