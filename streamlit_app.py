import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="Kmart AI Replenishment Prototype",
    layout="wide"
)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Kmart AI Replenishment")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Input",
        "AI Processing",
        "Output",
        "Order Action",
        "KPI Report"
    ]
)

st.sidebar.markdown("---")
st.sidebar.success("AI System Status: Operational")
st.sidebar.caption("Prototype demo only")

# =========================
# SESSION STATE
# =========================
if "forecast_run" not in st.session_state:
    st.session_state.forecast_run = False

# Default values
if "input_data" not in st.session_state:
    st.session_state.input_data = {
        "store": "Kmart Marion (SA)",
        "sku": "KM-BT-001",
        "product": "Bath Towel",
        "department": "Homewares",
        "current_stock": 12,
        "avg_daily_sales": 8,
        "promotion": "Yes",
        "lead_time": 5,
        "incoming_stock": 0,
        "shelf_status": "Low stock",
        "safety_stock_days": 2
    }

data = st.session_state.input_data

# =========================
# AI LOGIC
# =========================
promo_multiplier = 1.25 if data["promotion"] == "Yes" else 1.0

forecast_demand = round(
    data["avg_daily_sales"] * 7 * promo_multiplier
)

lead_time_demand = round(
    data["avg_daily_sales"] * data["lead_time"] * promo_multiplier
)

safety_stock = (
    data["avg_daily_sales"] * data["safety_stock_days"]
)

required_stock = lead_time_demand + safety_stock

stock_gap = required_stock - data["current_stock"]

recommended_order = max(
    math.ceil(stock_gap / 10) * 10,
    0
)

days_to_stockout = round(
    data["current_stock"] /
    max(data["avg_daily_sales"], 1),
    1
)

# Risk Logic
if days_to_stockout <= data["lead_time"]:
    risk = "High"
elif days_to_stockout <= data["lead_time"] + 2:
    risk = "Medium"
else:
    risk = "Low"

# Confidence Score
confidence = 88

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":

    st.title("Prototype Dashboard Overview")
    st.caption(
        "Overview of inventory risk, AI replenishment performance and workflow status"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Low-stock alerts", "12", "5 critical today")
    col2.metric("At-risk SKUs", "45", "12 high risk")
    col3.metric("On-shelf availability", "93.1%", "+2.1% vs last week")
    col4.metric("Auto orders", "18", "pending approval")

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        chart_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Availability": [84, 88, 93, 90, 92, 95, 94]
        })

        st.subheader("On-shelf availability trend")
        st.line_chart(
            chart_data.set_index("Day")
        )

    with right:
        st.subheader("Functional prototype workflow")

        st.markdown("""
        **1. Input**  
        SKU, stock, sales, promotion, lead time, shelf status

        **2. AI processing**  
        Demand forecast + stockout risk + reorder logic

        **3. Output**  
        Risk score, forecast demand, recommended quantity

        **4. Action**  
        Generate replenishment order for approval
        """)

    st.markdown("---")

    st.subheader("Top low-stock risks")

    dashboard_df = pd.DataFrame({
        "SKU": [
            "KM-BT-001",
            "KM-AF-008",
            "KM-SB-014",
            "KM-KT-023"
        ],
        "Product": [
            "Bath Towel",
            "Air Fryer",
            "Storage Box",
            "Kids T-shirt"
        ],
        "Category": [
            "Homewares",
            "Electronics",
            "Homewares",
            "Apparel"
        ],
        "Shelf Status": [
            "Low stock",
            "Low stock",
            "Low stock",
            "Normal"
        ],
        "Risk": [
            "High",
            "High",
            "Medium",
            "Low"
        ]
    })

    st.dataframe(
        dashboard_df,
        use_container_width=True
    )

# =========================
# INPUT PAGE
# =========================
elif page == "Input":

    st.title("Prototype Input Screen")
    st.caption(
        "Store manager enters SKU-level stock, sales, promotion and shelf-status data"
    )

    st.subheader("1. User Input")

    left, right = st.columns(2)

    with left:
        data["store"] = st.text_input(
            "Store",
            value=data["store"]
        )

        data["department"] = st.text_input(
            "Department",
            value=data["department"]
        )

        data["avg_daily_sales"] = st.number_input(
            "Average daily sales",
            min_value=1,
            value=data["avg_daily_sales"]
        )

        data["lead_time"] = st.number_input(
            "Supplier lead time (days)",
            min_value=1,
            value=data["lead_time"]
        )

        data["incoming_stock"] = st.number_input(
            "Incoming stock",
            min_value=0,
            value=data["incoming_stock"]
        )

    with right:
        data["sku"] = st.text_input(
            "Product SKU",
            value=data["sku"]
        )

        data["current_stock"] = st.number_input(
            "Current stock",
            min_value=0,
            value=data["current_stock"]
        )

        data["promotion"] = st.selectbox(
            "Promotion status",
            ["Yes", "No"]
        )

        data["shelf_status"] = st.selectbox(
            "Shelf status from computer vision",
            ["Low stock", "Normal", "Out of stock"]
        )

        data["safety_stock_days"] = st.number_input(
            "Safety stock rule (days)",
            min_value=1,
            value=data["safety_stock_days"]
        )

    if st.button("Run AI Forecast"):
        st.session_state.forecast_run = True
        st.success("AI replenishment forecast completed.")

    st.caption(
        "Input evidence: the prototype uses SKU, inventory, sales, promotion, supplier and shelf-status data to simulate the proposed Kmart replenishment workflow."
    )

# =========================
# AI PROCESSING
# =========================
elif page == "AI Processing":

    st.title("AI Processing Logic")
    st.caption(
        "Demand forecasting, stockout risk calculation and replenishment decision logic"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Promotion multiplier",
        promo_multiplier
    )

    c2.metric(
        "Forecast demand",
        f"{forecast_demand} units"
    )

    c3.metric(
        "Days to stockout",
        days_to_stockout
    )

    c4.metric(
        "Risk level",
        risk
    )

    st.markdown("---")

    process_df = pd.DataFrame({
        "Processing Step": [
            "Average daily sales x 7 x promotion multiplier",
            "Demand during lead time",
            "Safety stock rule",
            "Required stock",
            "Stock gap",
            "Recommended reorder quantity"
        ],
        "AI / Logic Result": [
            f"{forecast_demand} units",
            f"{lead_time_demand} units",
            f"{safety_stock} units",
            f"{required_stock} units",
            f"{stock_gap} units",
            f"{recommended_order} units"
        ]
    })

    st.dataframe(
        process_df,
        use_container_width=True
    )

    st.success(
        "AI explanation: Promotion increases expected demand. "
        "Computer vision detected low shelf status and the system predicts "
        "potential stockout risk before supplier delivery."
    )

# =========================
# OUTPUT PAGE
# =========================
elif page == "Output":

    st.title("AI Output Screen")
    st.caption(
        "The system converts input data into forecast, risk score and replenishment recommendation"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "7-day demand forecast",
        forecast_demand
    )

    col2.metric(
        "Stockout risk score",
        risk
    )

    col3.metric(
        "Recommended order",
        f"{recommended_order} units"
    )

    col4.metric(
        "AI confidence",
        f"{confidence}%"
    )

    st.markdown("---")

    output_df = pd.DataFrame({
        "AI Output": [
            "Product",
            "SKU",
            "Forecast demand",
            "Estimated stockout date",
            "Stockout risk"
        ],
        "Result": [
            data["product"],
            data["sku"],
            f"{forecast_demand} units in next 7 days",
            f"{days_to_stockout} days",
            risk
        ]
    })

    st.dataframe(
        output_df,
        use_container_width=True
    )

    st.warning(
        "Recommendation explanation: The system identifies elevated stockout risk "
        "because current stock is below forecast demand during supplier lead time. "
        "The recommendation is also influenced by promotion activity and low shelf visibility."
    )

# =========================
# ORDER ACTION
# =========================
elif page == "Order Action":

    st.title("Business Action: Generated Replenishment Order")
    st.caption(
        "AI output becomes an operational replenishment workflow for manager approval"
    )

    st.success(
        "The AI-generated order is prepared for ERP and supplier notification."
    )

    order_df = pd.DataFrame({
        "Order Field": [
            "Order ID",
            "Store",
            "Supplier",
            "SKU",
            "Order quantity",
            "Workflow outcome",
            "Governance control"
        ],
        "Details": [
            "KMT-RO-20260501",
            data["store"],
            "ABC Distribution",
            data["sku"],
            f"{recommended_order} units",
            "Prepared for ERP / supplier notification",
            "Human-in-the-loop approval"
        ]
    })

    st.dataframe(
        order_df,
        use_container_width=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.button("Send to ERP")
    c2.button("Email Supplier")
    c3.button("Download PO")
    c4.button("Cancel Order")

# =========================
# KPI REPORT
# =========================
elif page == "KPI Report":

    st.title("KPI Performance Report")

    st.metric(
        "Stockout reduction target",
        "25%"
    )

    st.metric(
        "Replenishment decision time improvement",
        "30%"
    )

    st.metric(
        "Target on-shelf availability",
        "95%"
    )

    kpi_df = pd.DataFrame({
        "KPI": [
            "Stockout Rate",
            "On-Shelf Availability",
            "Forecast Accuracy",
            "Order Processing Time"
        ],
        "Current": [
            "18%",
            "93.1%",
            "88%",
            "4.5 hrs"
        ],
        "Target": [
            "13%",
            "95%",
            "92%",
            "2 hrs"
        ]
    })

    st.dataframe(
        kpi_df,
        use_container_width=True
    )
