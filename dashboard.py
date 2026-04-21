"""
dashboard.py - Streamlit dashboard for energy demand forecast
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar la página
st.set_page_config(
    page_title="Colombia Energy Demand Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título
st.title("⚡ Colombia Energy Demand Forecast Dashboard")
st.markdown("---")

# Cargar datos
@st.cache_data
def load_data():
    """Load historical and forecast data"""
    try:
        # Cargar predicciones
        forecast = pd.read_csv('predictions/forecast_2025.csv')
        forecast['date'] = pd.to_datetime(forecast['date'])
        
        # Cargar datos históricos
        historical = pd.read_csv('data/processed/colombia_demand_2000_2024.csv')
        historical['date'] = pd.to_datetime(historical['date'])
        
        return historical, forecast
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

# Sidebar
st.sidebar.header("📊 Filters")
st.sidebar.markdown("---")

# Cargar datos
historical, forecast = load_data()

if historical is not None and forecast is not None:
    
    # Sidebar - Años disponibles
    available_years = sorted(historical['date'].dt.year.unique())
    
    # Seleccionar años por defecto (los últimos 2 años disponibles)
    default_years = available_years[-2:] if len(available_years) >= 2 else available_years
    
    selected_years = st.sidebar.multiselect(
        "Select Historical Years",
        available_years,
        default=default_years
    )
    
    # Si no hay años seleccionados, usar todos
    if not selected_years:
        selected_years = available_years
        st.sidebar.info("Showing all years")
    
    # Sidebar - Forecast days to show
    forecast_days = st.sidebar.slider(
        "Forecast Days to Display",
        min_value=30,
        max_value=365,
        value=90,
        step=30
    )
    
    # Sidebar - Metrics
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Key Metrics")
    
    # Métricas principales
    last_year = historical['date'].max().year
    next_year = forecast['date'].min().year
    
    avg_historical = historical['demand_kwh'].mean()
    avg_forecast = forecast['predicted_demand_kwh'].mean()
    growth = ((avg_forecast / avg_historical) - 1) * 100
    
    st.sidebar.metric(
        "Historical Avg (kWh)",
        f"{avg_historical/1e6:.1f}M",
        delta=None
    )
    st.sidebar.metric(
        f"Forecast {next_year} Avg (kWh)",
        f"{avg_forecast/1e6:.1f}M",
        delta=f"{growth:.1f}% vs historical"
    )
    
    # Main content - Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Forecast", 
        "📊 Historical Trends", 
        "📅 Monthly Analysis",
        "📋 Data Tables"
    ])
    
    # Tab 1: Forecast
    with tab1:
        st.header(f"Energy Demand Forecast for {next_year}")
        
        # Filter forecast days
        forecast_filtered = forecast.head(forecast_days)
        
        # Gráfico de predicciones
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=forecast_filtered['date'],
            y=forecast_filtered['predicted_demand_kwh'],
            mode='lines',
            name='Forecast',
            line=dict(color='red', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_filtered['date'],
            y=forecast_filtered['upper_bound_kwh'],
            mode='lines',
            name='Upper Bound',
            line=dict(color='lightcoral', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_filtered['date'],
            y=forecast_filtered['lower_bound_kwh'],
            mode='lines',
            name='Lower Bound',
            line=dict(color='lightcoral', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(255, 99, 71, 0.2)'
        ))
        
        fig.update_layout(
            title=f"Daily Energy Demand Forecast - First {forecast_days} Days of {next_year}",
            xaxis_title="Date",
            yaxis_title="Demand (kWh)",
            hovermode='x unified',
            height=500,
            yaxis=dict(tickformat='.0f', ticksuffix=' kWh')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Predicciones destacadas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                f"Average Demand {next_year}",
                f"{avg_forecast/1e6:.1f}M kWh",
                delta=f"{growth:.1f}%"
            )
        
        with col2:
            max_demand = forecast['predicted_demand_kwh'].max()
            max_date = forecast.loc[forecast['predicted_demand_kwh'].idxmax(), 'date']
            st.metric(
                "Peak Demand",
                f"{max_demand/1e6:.1f}M kWh",
                delta=f"on {max_date.strftime('%b %d')}"
            )
        
        with col3:
            min_demand = forecast['predicted_demand_kwh'].min()
            min_date = forecast.loc[forecast['predicted_demand_kwh'].idxmin(), 'date']
            st.metric(
                "Lowest Demand",
                f"{min_demand/1e6:.1f}M kWh",
                delta=f"on {min_date.strftime('%b %d')}"
            )
    
    # Tab 2: Historical Trends
    with tab2:
        st.header("Historical Demand Trends (2000-2024)")
        
        # Filtrar datos históricos por años seleccionados
        historical_filtered = historical[historical['date'].dt.year.isin(selected_years)]
        
        if not historical_filtered.empty:
            # Gráfico histórico
            fig2 = px.line(
                historical_filtered,
                x='date',
                y='demand_kwh',
                title="Historical Energy Demand",
                labels={'date': 'Date', 'demand_kwh': 'Demand (kWh)'}
            )
            
            fig2.update_layout(
                height=500,
                yaxis=dict(tickformat='.0f', ticksuffix=' kWh')
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No data available for selected years")
        
        # Tendencia anual
        st.subheader("Yearly Average Demand Trend")
        
        yearly_avg = historical.groupby(historical['date'].dt.year)['demand_kwh'].mean().reset_index()
        yearly_avg.columns = ['year', 'avg_demand']
        
        fig3 = px.bar(
            yearly_avg,
            x='year',
            y='avg_demand',
            title="Average Demand by Year",
            labels={'year': 'Year', 'avg_demand': 'Average Demand (kWh)'},
            color='avg_demand',
            color_continuous_scale='Viridis'
        )
        
        fig3.update_layout(
            height=400,
            yaxis=dict(tickformat='.0f', ticksuffix=' kWh')
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # Tab 3: Monthly Analysis
    with tab3:
        st.header("Monthly Demand Analysis")
        
        # Crear columnas de mes
        historical_copy = historical.copy()
        forecast_copy = forecast.copy()
        
        historical_copy['month'] = historical_copy['date'].dt.month
        forecast_copy['month'] = forecast_copy['date'].dt.month
        
        # Promedios mensuales históricos
        monthly_historical = historical_copy.groupby('month')['demand_kwh'].mean().reset_index()
        monthly_forecast = forecast_copy.groupby('month')['predicted_demand_kwh'].mean().reset_index()
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        monthly_historical['month_name'] = monthly_historical['month'].apply(lambda x: months[x-1])
        monthly_forecast['month_name'] = monthly_forecast['month'].apply(lambda x: months[x-1])
        
        # Gráfico comparativo
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=monthly_historical['month_name'],
            y=monthly_historical['demand_kwh'],
            name='Historical Average (2000-2024)',
            marker_color='blue',
            opacity=0.7
        ))
        
        fig4.add_trace(go.Bar(
            x=monthly_forecast['month_name'],
            y=monthly_forecast['predicted_demand_kwh'],
            name=f'Forecast {next_year}',
            marker_color='red',
            opacity=0.7
        ))
        
        fig4.update_layout(
            title="Monthly Demand Comparison: Historical vs Forecast",
            xaxis_title="Month",
            yaxis_title="Average Demand (kWh)",
            barmode='group',
            height=500,
            yaxis=dict(tickformat='.0f', ticksuffix=' kWh')
        )
        
        st.plotly_chart(fig4, use_container_width=True)
        
        # Tabla mensual
        st.subheader("Monthly Summary Table")
        
        monthly_comparison = pd.DataFrame({
            'Month': months,
            'Historical Avg (kWh)': monthly_historical['demand_kwh'].values,
            f'Forecast {next_year} (kWh)': monthly_forecast['predicted_demand_kwh'].values
        })
        
        monthly_comparison['Historical Avg (MWh)'] = monthly_comparison['Historical Avg (kWh)'] / 1e6
        monthly_comparison[f'Forecast {next_year} (MWh)'] = monthly_comparison[f'Forecast {next_year} (kWh)'] / 1e6
        monthly_comparison['Growth (%)'] = ((monthly_comparison[f'Forecast {next_year} (kWh)'] / 
                                               monthly_comparison['Historical Avg (kWh)']) - 1) * 100
        
        st.dataframe(
            monthly_comparison[['Month', 'Historical Avg (MWh)', f'Forecast {next_year} (MWh)', 'Growth (%)']],
            use_container_width=True,
            hide_index=True
        )
    
    # Tab 4: Data Tables
    with tab4:
        st.header("Data Tables")
        
        # Selector de tabla
        table_choice = st.radio(
            "Select table to view:",
            ["Forecast Data", "Historical Data"],
            horizontal=True
        )
        
        if table_choice == "Forecast Data":
            st.subheader(f"Energy Demand Forecast for {next_year}")
            
            # Formatear datos
            display_forecast = forecast.copy()
            display_forecast['date'] = display_forecast['date'].dt.strftime('%Y-%m-%d')
            display_forecast['predicted_demand_kwh'] = display_forecast['predicted_demand_kwh'].round(0).astype(int)
            display_forecast['lower_bound_kwh'] = display_forecast['lower_bound_kwh'].round(0).astype(int)
            display_forecast['upper_bound_kwh'] = display_forecast['upper_bound_kwh'].round(0).astype(int)
            
            # Mostrar tabla
            st.dataframe(
                display_forecast,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Botón de descarga
            csv = display_forecast.to_csv(index=False)
            st.download_button(
                label="📥 Download Forecast CSV",
                data=csv,
                file_name=f"forecast_{next_year}.csv",
                mime="text/csv"
            )
        
        else:
            st.subheader("Historical Demand Data (2000-2024)")
            
            # Formatear datos históricos
            display_historical = historical.copy()
            display_historical['date'] = display_historical['date'].dt.strftime('%Y-%m-%d')
            display_historical['demand_kwh'] = display_historical['demand_kwh'].round(0).astype(int)
            
            # Mostrar tabla
            st.dataframe(
                display_historical,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Botón de descarga
            csv = display_historical.to_csv(index=False)
            st.download_button(
                label="📥 Download Historical CSV",
                data=csv,
                file_name="historical_demand_2000_2024.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: gray;'>"
        f"Data source: XM (Operador del Sistema Interconectado Nacional de Colombia)<br>"
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>"
        f"Forecast model: Facebook Prophet | MAE: 5.94M kWh"
        f"</div>",
        unsafe_allow_html=True
    )

else:
    st.error("Could not load data. Make sure the files exist in the correct paths.")
    st.info("Run `python run_forecast.py` first to generate the forecast data.")