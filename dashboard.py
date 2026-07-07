"""
dashboard.py - Streamlit dashboard for energy demand forecast
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import glob
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
        # Buscar predicciones más recientes
        forecast_files = glob.glob('predictions/forecast_*.csv')
        if not forecast_files:
            st.error("No forecast files found. Run run_forecast.py first.")
            return None, None
        
        latest_forecast = sorted(forecast_files)[-1]
        forecast = pd.read_csv(latest_forecast)
        forecast['date'] = pd.to_datetime(forecast['date'])
        
        # Buscar histórico más reciente
        historical_files = glob.glob('data/processed/colombia_demand_*.csv')
        if not historical_files:
            st.error("No historical data found. Run run_forecast.py first.")
            return None, None
        
        latest_historical = sorted(historical_files)[-1]
        historical = pd.read_csv(latest_historical)
        historical['date'] = pd.to_datetime(historical['date'])
        
        return historical, forecast
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

# Sidebar
st.sidebar.header("📊 Filters")
st.sidebar.markdown("---")

historical, forecast = load_data()

if historical is not None and forecast is not None:
    
    # Sidebar - años disponibles
    available_years = sorted(historical['date'].dt.year.unique())
    default_years = available_years[-2:] if len(available_years) >= 2 else available_years
    
    selected_years = st.sidebar.multiselect(
        "Select Historical Years",
        available_years,
        default=default_years
    )
    
    if not selected_years:
        selected_years = available_years
    
    # Días de forecast a mostrar
    forecast_days = st.sidebar.slider(
        "Forecast Days to Display",
        min_value=30,
        max_value=365,
        value=90,
        step=30
    )
    
    # Métricas en sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Key Metrics")
    
    last_year = historical['date'].max().year
    forecast_year = forecast['date'].dt.year.iloc[0]
    
    avg_historical = historical['demand_kwh'].mean()
    avg_forecast = forecast['predicted_demand_kwh'].mean()
    growth = ((avg_forecast / avg_historical) - 1) * 100
    
    st.sidebar.metric(
        "Historical Avg (kWh)",
        f"{avg_historical/1e6:.1f}M",
        delta=None
    )
    st.sidebar.metric(
        f"Forecast Avg (kWh)",
        f"{avg_forecast/1e6:.1f}M",
        delta=f"{growth:.1f}% vs historical"
    )
    
    # Pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Forecast",
        "📊 Historical Trends",
        "📅 Seasonal Analysis",
        "📉 Growth Analysis",
        "📋 Data Tables"
    ])
    
    # ========================================
    # TAB 1: FORECAST
    # ========================================
    with tab1:
        st.header(f"Energy Demand Forecast")
        
        forecast_filtered = forecast.head(forecast_days)
        
        # Gráfico 1: Forecast con intervalos de confianza
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=forecast_filtered['date'],
            y=forecast_filtered['predicted_demand_kwh'],
            mode='lines',
            name='Forecast',
            line=dict(color='#FF6B35', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_filtered['date'],
            y=forecast_filtered['upper_bound_kwh'],
            mode='lines',
            name='Upper Bound',
            line=dict(color='#FFB088', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_filtered['date'],
            y=forecast_filtered['lower_bound_kwh'],
            mode='lines',
            name='Lower Bound',
            line=dict(color='#FFB088', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(255, 107, 53, 0.15)'
        ))
        
        fig.update_layout(
            title=f"Daily Energy Demand Forecast - Next {forecast_days} Days",
            xaxis_title="Date",
            yaxis_title="Demand (kWh)",
            hovermode='x unified',
            height=500,
            yaxis=dict(tickformat='.0f', ticksuffix=' kWh'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas destacadas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Average Demand",
                f"{avg_forecast/1e6:.1f}M kWh",
                delta=f"{growth:.1f}%"
            )
        
        with col2:
            max_demand = forecast['predicted_demand_kwh'].max()
            max_date = forecast.loc[forecast['predicted_demand_kwh'].idxmax(), 'date']
            st.metric(
                "Peak Demand",
                f"{max_demand/1e6:.1f}M kWh",
                delta=f"on {max_date.strftime('%b %d, %Y')}"
            )
        
        with col3:
            min_demand = forecast['predicted_demand_kwh'].min()
            min_date = forecast.loc[forecast['predicted_demand_kwh'].idxmin(), 'date']
            st.metric(
                "Lowest Demand",
                f"{min_demand/1e6:.1f}M kWh",
                delta=f"on {min_date.strftime('%b %d, %Y')}"
            )
        
        with col4:
            confidence = ((forecast['upper_bound_kwh'] - forecast['lower_bound_kwh']) / forecast['predicted_demand_kwh']).mean() * 100
            st.metric(
                "Avg Confidence Interval",
                f"±{confidence:.1f}%",
                delta=None
            )
    
    # ========================================
    # TAB 2: HISTORICAL TRENDS
    # ========================================
    with tab2:
        st.header("Historical Demand Trends")
        
        # Filtrar datos
        historical_filtered = historical[historical['date'].dt.year.isin(selected_years)]
        
        # Gráfico 2: Serie histórica completa con forecast
        st.subheader("Full Historical Series with Forecast")
        
        # Crear dataset combinado
        combined = pd.concat([
            historical_filtered[['date', 'demand_kwh']].rename(columns={'demand_kwh': 'value'}),
            forecast[['date', 'predicted_demand_kwh']].rename(columns={'predicted_demand_kwh': 'value'})
        ]).sort_values('date')
        
        combined['type'] = ['Historical'] * len(historical_filtered) + ['Forecast'] * len(forecast)
        
        fig2 = px.line(
            combined,
            x='date',
            y='value',
            color='type',
            title="Historical Demand & Forecast",
            labels={'value': 'Demand (kWh)', 'date': 'Date'},
            color_discrete_map={'Historical': '#2E86AB', 'Forecast': '#FF6B35'}
        )
        
        fig2.update_layout(
            height=400,
            yaxis=dict(tickformat='.0f', ticksuffix=' kWh'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico 3: Promedio anual
        st.subheader("Yearly Average Demand")
        
        yearly_avg = historical.groupby(historical['date'].dt.year)['demand_kwh'].mean().reset_index()
        yearly_avg.columns = ['year', 'avg_demand']
        
        # Agregar forecast anual (promedio de todo el forecast)
        forecast_avg = forecast['predicted_demand_kwh'].mean()
        forecast_year = forecast['date'].dt.year.iloc[0]
        
        yearly_avg_combined = pd.concat([
            yearly_avg,
            pd.DataFrame({'year': [forecast_year], 'avg_demand': [forecast_avg]})
        ])
        
        fig3 = px.bar(
            yearly_avg_combined,
            x='year',
            y='avg_demand',
            title="Average Demand by Year (Historical + Forecast)",
            labels={'year': 'Year', 'avg_demand': 'Average Demand (kWh)'},
            color='avg_demand',
            color_continuous_scale='Viridis',
            text_auto='.1f'
        )
        
        fig3.update_layout(
            height=400,
            yaxis=dict(tickformat='.0f', ticksuffix=' kWh'),
            showlegend=False
        )
        
        fig3.update_traces(texttemplate='%{text:.1f}M', textposition='outside')
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # ========================================
    # TAB 3: SEASONAL ANALYSIS
    # ========================================
    with tab3:
        st.header("Seasonal Demand Analysis")
        
        # Preparar datos
        historical['month'] = historical['date'].dt.month
        historical['day_of_week'] = historical['date'].dt.dayofweek
        historical['year'] = historical['date'].dt.year
        
        forecast['month'] = forecast['date'].dt.month
        forecast['day_of_week'] = forecast['date'].dt.dayofweek
        forecast['year'] = forecast['date'].dt.year
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Gráfico 4: Mapa de calor estacional (histórico)
        st.subheader("Historical Seasonal Pattern (2000-2024)")
        
        # Crear matriz de calor: mes vs día de semana
        heatmap_data = historical.groupby(['month', 'day_of_week'])['demand_kwh'].mean().unstack()
        heatmap_data.columns = days
        heatmap_data.index = months
        
        fig4 = px.imshow(
            heatmap_data,
            text_auto='.1f',
            title="Demand by Month and Day of Week (Historical)",
            labels=dict(x="Day of Week", y="Month", color="Avg Demand (kWh)"),
            color_continuous_scale='Viridis',
            aspect="auto",
            height=450
        )
        
        fig4.update_layout(
            xaxis=dict(tickangle=0),
            yaxis=dict(tickangle=0)
        )
        
        st.plotly_chart(fig4, use_container_width=True)
        
        # Gráfico 5: Monthly comparison historical vs forecast
        st.subheader("Monthly Demand Comparison")
        
        monthly_historical = historical.groupby('month')['demand_kwh'].mean().reset_index()
        monthly_forecast = forecast.groupby('month')['predicted_demand_kwh'].mean().reset_index()
        
        monthly_historical['month_name'] = monthly_historical['month'].apply(lambda x: months[x-1])
        monthly_forecast['month_name'] = monthly_forecast['month'].apply(lambda x: months[x-1])
        
        fig5 = go.Figure()
        
        fig5.add_trace(go.Bar(
            x=monthly_historical['month_name'],
            y=monthly_historical['demand_kwh'],
            name='Historical Average (2000-2026)',
            marker_color='#2E86AB',
            opacity=0.7
        ))
        
        fig5.add_trace(go.Bar(
            x=monthly_forecast['month_name'],
            y=monthly_forecast['predicted_demand_kwh'],
            name=f'Forecast',
            marker_color='#FF6B35',
            opacity=0.7
        ))
        
        fig5.update_layout(
            title="Monthly Demand: Historical vs Forecast",
            xaxis_title="Month",
            yaxis_title="Average Demand (kWh)",
            barmode='group',
            height=450,
            yaxis=dict(tickformat='.0f', ticksuffix=' kWh'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig5, use_container_width=True)
    
    # ========================================
    # TAB 4: GROWTH ANALYSIS
    # ========================================
    with tab4:
        st.header("Growth & Trend Analysis")
        
        # Gráfico 6: Crecimiento interanual
        st.subheader("Year-over-Year Growth")
        
        # Calcular crecimiento interanual
        yearly_growth = historical.groupby(historical['date'].dt.year)['demand_kwh'].mean().reset_index()
        yearly_growth.columns = ['year', 'avg_demand']
        yearly_growth['growth'] = yearly_growth['avg_demand'].pct_change() * 100
        yearly_growth = yearly_growth.dropna()
        
        fig6 = px.bar(
            yearly_growth,
            x='year',
            y='growth',
            title="Year-over-Year Growth Rate (%)",
            labels={'year': 'Year', 'growth': 'Growth (%)'},
            color='growth',
            color_continuous_scale='RdYlGn',
            text_auto='.1f'
        )
        
        fig6.update_layout(
            height=400,
            yaxis=dict(ticksuffix='%'),
            showlegend=False
        )
        
        fig6.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        
        st.plotly_chart(fig6, use_container_width=True)
        
        # Gráfico 7: Histograma de demanda
        st.subheader("Demand Distribution")
        
        fig7 = go.Figure()
        
        fig7.add_trace(go.Histogram(
            x=historical['demand_kwh'],
            name='Historical',
            marker_color='#2E86AB',
            opacity=0.7,
            nbinsx=40
        ))
        
        fig7.add_trace(go.Histogram(
            x=forecast['predicted_demand_kwh'],
            name='Forecast',
            marker_color='#FF6B35',
            opacity=0.7,
            nbinsx=40
        ))
        
        fig7.update_layout(
            title="Demand Distribution: Historical vs Forecast",
            xaxis_title="Demand (kWh)",
            yaxis_title="Frequency (days)",
            height=400,
            yaxis=dict(tickformat='.0f'),
            xaxis=dict(tickformat='.0f', ticksuffix=' kWh'),
            barmode='overlay',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig7, use_container_width=True)
        
        # Tabla de crecimiento
        st.subheader("Growth Summary by Period")
        
        periods = [
            ('2000-2005', historical[historical['date'].dt.year <= 2005]['demand_kwh'].mean()),
            ('2006-2010', historical[(historical['date'].dt.year >= 2006) & (historical['date'].dt.year <= 2010)]['demand_kwh'].mean()),
            ('2011-2015', historical[(historical['date'].dt.year >= 2011) & (historical['date'].dt.year <= 2015)]['demand_kwh'].mean()),
            ('2016-2020', historical[(historical['date'].dt.year >= 2016) & (historical['date'].dt.year <= 2020)]['demand_kwh'].mean()),
            ('2021-2026', historical[historical['date'].dt.year >= 2021]['demand_kwh'].mean()),
            ('Forecast', forecast['predicted_demand_kwh'].mean())
        ]
        
        growth_df = pd.DataFrame(periods, columns=['Period', 'Avg Demand (kWh)'])
        growth_df['Avg Demand (MWh)'] = growth_df['Avg Demand (kWh)'] / 1e6
        growth_df['Growth (%)'] = growth_df['Avg Demand (kWh)'].pct_change() * 100
        
        st.dataframe(
            growth_df[['Period', 'Avg Demand (MWh)', 'Growth (%)']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'Avg Demand (MWh)': st.column_config.NumberColumn(format="%.1f M"),
                'Growth (%)': st.column_config.NumberColumn(format="%.1f%%")
            }
        )
    
    # ========================================
    # TAB 5: DATA TABLES
    # ========================================
    with tab5:
        st.header("Data Tables")
        
        table_choice = st.radio(
            "Select table to view:",
            ["Forecast Data", "Historical Data"],
            horizontal=True
        )
        
        if table_choice == "Forecast Data":
            st.subheader("Energy Demand Forecast")
            
            display_forecast = forecast.copy()
            display_forecast['date'] = display_forecast['date'].dt.strftime('%Y-%m-%d')
            display_forecast['predicted_demand_kwh'] = display_forecast['predicted_demand_kwh'].round(0).astype(int)
            display_forecast['lower_bound_kwh'] = display_forecast['lower_bound_kwh'].round(0).astype(int)
            display_forecast['upper_bound_kwh'] = display_forecast['upper_bound_kwh'].round(0).astype(int)
            
            st.dataframe(
                display_forecast,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            csv = display_forecast.to_csv(index=False)
            st.download_button(
                label="📥 Download Forecast CSV",
                data=csv,
                file_name=f"forecast_{forecast['date'].dt.year.iloc[0]}.csv",
                mime="text/csv"
            )
        
        else:
            st.subheader("Historical Demand Data")
            
            display_historical = historical.copy()
            display_historical['date'] = display_historical['date'].dt.strftime('%Y-%m-%d')
            display_historical['demand_kwh'] = display_historical['demand_kwh'].round(0).astype(int)
            
            st.dataframe(
                display_historical,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            csv = display_historical.to_csv(index=False)
            st.download_button(
                label="📥 Download Historical CSV",
                data=csv,
                file_name=f"historical_demand_{historical['date'].min().year}_{historical['date'].max().year}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: gray; font-size: 0.9em;'>
            <b>Data source:</b> XM (Operador del Sistema Interconectado Nacional de Colombia)<br>
            <b>Historical data:</b> {historical['date'].min().year} - {historical['date'].max().year} ({len(historical):,} records)<br>
            <b>Forecast period:</b> {forecast['date'].min().date()} to {forecast['date'].max().date()}<br>
            <b>Model:</b> Facebook Prophet | <b>MAE:</b> 5.94M kWh<br>
            <b>Last updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.error("Could not load data. Make sure the files exist in the correct paths.")
    st.info("Run `python run_forecast.py` first to generate the forecast data.")
