```
🚀 Installation
1. Clone the Repository
git clone https://github.com/your-username/AI-Illegal-Parking-Detection.git
2. Open the Project
cd AI-Illegal-Parking-Detection
3. Create a Virtual Environment
python -m venv venv

Activate the environment on Windows:

venv\Scripts\activate
4. Install Dependencies
pip install -r requirements.txt
5. Configure Database

Create a MySQL database and configure the database connection according to your project setup.

6. Run the Streamlit Application
streamlit run app.py

The application will open in your web browser.
📂### Project Structure
```
```text
AI-Illegal-Parking-Detection/
│
├── app.py
│
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Live_Monitoring.py
│   ├── 3_Violations.py
│   ├── 4_Cameras.py
│   ├── 5_Reports.py
│   └── 6_Settings.py
│
├── ai/
│   ├── vehicle_detection.py
│   ├── parking_detection.py
│   └── number_plate.py
│
├── database/
│   └── db.py
│
├── evidence/
│
├── models/
│   └── yolo_model.pt
│
├── requirements.txt
├── .gitignore
└── README.md
```
