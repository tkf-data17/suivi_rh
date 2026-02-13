def get_custom_css():
    return """
    <style>
        /* Modern Color Palette & Variables */
        :root {
            --primary-color: #2E865F; /* Green from the excel header */
            --secondary-color: #e8f5e9;
            --accent-color: #4CAF50;
            --text-color: #333333;
            --bg-color: #f8f9fa;
        }

        /* Main Container Styling */
        .stApp {
            background-color: var(--bg-color);
            font-family: 'Inter', sans-serif;
        }

        /* Header Styling */
        h1 {
            color: var(--primary-color);
            font-weight: 700;
            text-align: center;
            padding-bottom: 2rem;
            border-bottom: 2px solid var(--primary-color);
            margin-bottom: 2rem;
        }
        
        h2, h3 {
            color: var(--text-color);
            font-weight: 600;
        }

        /* Input Fields Styling */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            padding: 10px;
            transition: all 0.3s ease;
        }

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus,
        .stDateInput > div > div > input:focus,
        .stTimeInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(46, 134, 95, 0.2);
        }

        /* Button Styling */
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }

        .stButton > button:hover {
            background-color: #256b4d;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }

        /* DataFrame/Table Styling */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            background: white;
            padding: 1rem;
        }

        /* Custom Information Cards */
        .info-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            border-left: 4px solid var(--primary-color);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: white;
            border-right: 1px solid #f0f0f0;
        }

        /* Hide Streamlit Header & Footer */
        /* Hide Streamlit Header & Footer but allow sidebar */
        header {
            /* visibility: hidden; - This hides the hamburger menu which controls sidebar */
            /* Use other ways to hide clutter if needed, or just allow it */
            background: transparent;
        }
        
        footer {
            visibility: hidden;
            height: 0px;
        }

        /* Adjust Main Content Padding to push content up */
        /* Adjust Main Content Padding to push content up */
        .block-container {
            padding-top: 1.5rem !important; 
            padding-bottom: 2rem !important;
            max-width: 95% !important; 
        }
        
        /* Reduce spacing of the top header area */
        [data-testid="stHeader"] {
            height: 3rem; /* Force reduce header height if possible */
            background: transparent;
        }
        
        /* Adjust for sidebar menu if needed */
        [data-testid="stSidebarNav"] {
            padding-top: 1rem;
        }
    </style>
    """
