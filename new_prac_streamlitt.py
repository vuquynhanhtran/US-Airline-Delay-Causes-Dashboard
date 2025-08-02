#Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import calendar
from pandas.api.types import CategoricalDtype


#Define setting for app by giving a page title and icon to display on the browser.
st.set_page_config(
    page_title='USA Airline Delay Causes',
    page_icon='',
    layout='wide',
    initial_sidebar_state='expanded',
)

#'Hey Streamlit, please dont reload this if the file doesnt change my computer is old enough'
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

#Load data
df_main = pd.read_csv('/Users/quynhanh/Downloads/Airline_Delay_Cause.csv', low_memory=False)
df_main['airport'] = df_main['airport'].str.upper()

#We also need to load another dataset for airport name including states so as to make a choropleth map
df_airports = pd.read_csv('/Users/quynhanh/Downloads/archive/airports.csv')
df_airports['IATA_CODE'] = df_airports['IATA_CODE'].str.upper()

#Filter df_main to only keep rows that match valid airport codes
valid_airports = set(df_airports['IATA_CODE'])
df_main_filtered = df_main[df_main['airport'].isin(valid_airports)]

# Merge state info into df_main
df_merged = df_main_filtered.merge(
    df_airports[['IATA_CODE', 'STATE']],
    how='left',
    left_on='airport',
    right_on='IATA_CODE'
)

st.title('USA Airline Delay Causes')
# st.subheader('')

#Add a sidebar: Anything indented under this gets pinned to the side
with st.sidebar:
    st.title('Menu')  # Title in the sidebar
    year_list = sorted(df_merged['year'].unique(), reverse=True)  # Dropdown from most recent year
    selected_year = st.selectbox("Select Year", year_list)
    df_selected_year = df_merged[df_merged['year'] == selected_year]  # Choose the data in the selected year
    
    #Update: Sidebar - Add month selector
    months_list = list(range(1,13))
    selected_month = st.selectbox('Select Month', ['All'] + months_list)
    if selected_month != 'All':
        df_selected = df_selected_year[df_selected_year['month'] == selected_month]
    else:
        df_selected = df_selected_year.copy()
    
    #Update: Add a box of information to show the number of delays and cancellations in the year
     # Add total number of delays and cancellations in the sidebar
    total_delays = df_selected['arr_del15'].sum()
    total_cancellations = df_selected['arr_cancelled'].sum()
    
    st.subheader(f"Summary for {selected_month}/{selected_year}" if selected_month != 'All' else f"Summary for {selected_year}")
    comparison_year = selected_year -1
    df_last_year = df_merged[df_merged['year'] == comparison_year]
    if selected_month == 'All':
        prev_delays = df_last_year['arr_del15'].sum()
        prev_cancellations = df_last_year['arr_cancelled'].sum()
    else:
        df_last_year_month = df_last_year[df_last_year['month']==selected_month]
        prev_delays=df_last_year_month['arr_del15'].sum()
        prev_cancellations=df_last_year_month['arr_cancelled'].sum()
    delta_delays = total_delays - prev_delays
    delta_cancellations = total_cancellations - prev_cancellations
    
    delay_pct = (delta_delays / prev_delays * 100) if prev_delays != 0 else 0
    cancel_pct = (delta_cancellations / prev_cancellations * 100) if prev_cancellations != 0 else 0
    
    delay_change = f'{delay_pct:+.2f}%'
    cancel_change = f'{cancel_pct:+.2f}%'

    st.metric("Total Delays", f"{int(total_delays):,}", delay_change, border = True)
    st.metric("Total Cancellations", f"{int(total_cancellations):,}", cancel_change, border = True)
    

# Create columns
col1, col2, col3 = st.columns([0.75, 1.25, 1.75])


# -------------------- COLUMN 1 --------------------
with col1:
    with st.container(border=True):
        #-----Top delay causes------
        st.subheader("Top Delay Causes")
        
        carrier = df_selected['carrier_ct'].sum()
        late_aircraft = df_selected['late_aircraft_ct'].sum()
        nas = df_selected['nas_ct'].sum()
        weather = df_selected['weather_ct'].sum()
        security = df_selected['security_ct'].sum()
        
        raw_data = [
            ('Carrier', carrier),
            ('Late Aircraft', late_aircraft),
            ('NAS', nas),
            ('Weather', weather),
            ('Security', security),
        ]
        
        total_delays = sum(v for _, v in raw_data)
        filtered_data = [(label, v) for label, v in raw_data if (v / total_delays) >= 0.05]
        filtered_data.sort(key=lambda x: x[1], reverse=True)
        labels, sizes = zip(*filtered_data)

        colors = ['#a4133c', '#c9184a', '#ff8fa3','#ff758f','#ff8fa3','#ffccd5'][:len(sizes)]

        fig, ax = plt.subplots(figsize=(3.5, 3.5))
        fig.patch.set_alpha(0)  # transparent background
        ax.set_facecolor("none")  # also transparent inside the pie

        
        def make_autopct(values,labels):
            def my_autopct(pct):
                total=sum(values)
                value=int(round(pct*total)/100)
                label = labels[my_autopct.idx]
                my_autopct.idx+=1
                return f'{label}\n{pct:.1f}%'
            my_autopct.idx=0
            return my_autopct
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct=make_autopct(sizes, labels),
            startangle=90,
            textprops={
                'fontsize': 10,
                'color': 'white'
                }
            )

        
        # Center the pie by manually adjusting axis position (zoom)
        ax.set_position([0.1, 0.1, 0.8, 0.8])
        ax.axis('equal')
        st.pyplot(fig)


    # -- Donuts for Delayed and Cancelled Flights --
    total_flights = df_selected['arr_flights'].sum()
    total_delayed = df_selected['arr_del15'].sum()
    total_cancelled = df_selected['arr_cancelled'].sum()

    delay_ratio = total_delayed / total_flights * 100
    cancel_ratio = total_cancelled / total_flights * 100

    # -- Delayed --
    with st.container(border=True):
        st.subheader("Delayed Flights")
        fig_delay = go.Figure(go.Indicator(
            mode="gauge+number",
            value=delay_ratio,
            number={'suffix': "%", 'font': {'size': 34, 'color': '#218380'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#218380", 'thickness': 0.25},
                'bgcolor': "#eee",
                'borderwidth': 0,
                'threshold': {
                    'line': {'color': "#218380", 'width': 2},
                    'thickness': 0.75,
                    'value': delay_ratio
                }
            },
            title={'text': "Proportion Delayed", 'font': {'size': 20}}
        ))
        fig_delay.update_layout(
            height=300, 
            margin=dict(t=20, b=20), 
            #paper_bgcolor='#ffffff'
            )  # entire card background
        st.plotly_chart(fig_delay, use_container_width=True)
        # st.markdown("---")

    # -- Cancelled --
    with st.container(border=True):
        st.subheader("Cancelled Flights")
        fig_cancel = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cancel_ratio,
            number={'suffix': "%", 'font': {'size': 34, 'color': '#218380'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#218380", 'thickness': 0.25},
                'bgcolor': "#eee",
                'borderwidth': 0,
                'threshold': {
                    'line': {'color': "#218380", 'width': 2},
                    'thickness': 0.75,
                    'value': cancel_ratio
                }
            },
            title={'text': "Proportion Cancelled", 'font': {'size': 20}}))
        fig_cancel.update_layout(
            height=300, 
            margin=dict(t=20, b=20), 
            # paper_bgcolor='#ffffff'
        )
        st.plotly_chart(fig_cancel, use_container_width=True)
        

# -------------------- COLUMN 2 --------------------
#Note for column 2 if a month is selected

with col2:
    with st.container(border=True):
        st.subheader("Monthly Trends: Top Delay Causes")
        # Columns for this shit 
        delay_keys = ['carrier_ct', 'late_aircraft_ct', 'nas_ct', 'weather_ct']
        delay_labels = {
            'carrier_ct': 'Air Carrier',
            'late_aircraft_ct': 'Late Aircraft',
            'nas_ct': 'NAS',
            'weather_ct': 'Weather'
        }
        # Monthly groups and their respected sums
        monthly_delay = df_selected_year.groupby('month')[delay_keys].sum().reset_index()
        monthly_delay['month_name'] = monthly_delay['month'].apply(lambda x: calendar.month_abbr[int(x)])
        # Turn it into a table that the graph can read
        monthly_long = monthly_delay.melt(id_vars=['month','month_name'], var_name='Cause', value_name='Delays')
        # Replace raw column names with clean labels
        monthly_long['Cause'] = monthly_long['Cause'].map(delay_labels)
        # Plot
        fig = px.line(
            monthly_long,
            x='month_name',
            y='Delays',
            color='Cause',
            markers=True,
            color_discrete_map={
                'Air Carrier': '#d81159',
                'Late Aircraft': '#8f2d56',
                'NAS': '#218380',
                'Weather': '#ffbc42'
            },
            labels={'month': 'Month', 'Delays': 'Delay Count'},
            hover_name = 'Cause',
            hover_data = {'month':True, 'Delays':':.2f'} #Delay values round to 2 decimals
        )
        
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Delays: %{y:,.0f}<extra></extra>")

        fig.update_layout(
            xaxis_title='',
            yaxis_title='',
            hovermode='x unified',
            legend_title='Cause',
            # plot_bgcolor='#ffffff',
            # paper_bgcolor='#ffffff',
            xaxis=dict(tickmode='linear', tick0=1, dtick=1))


        st.plotly_chart(fig, use_container_width=True)


    with st.container(border=True):
        st.subheader("Monthly Trends: Cancellations")
        #Monthly cancellations
        monthly_cancel = df_selected_year.groupby('month')['arr_cancelled'].sum().reset_index()
        monthly_cancel['month_name'] = monthly_cancel['month'].apply(lambda x: calendar.month_abbr[int(x)])
        
        #Ensure months are in Jan-Dec order
        month_order = list(calendar.month_abbr)[1:]
        monthly_cancel['month_name'] = monthly_cancel['month_name'].astype(
            CategoricalDtype(categories=month_order,ordered=True))
        monthly_cancel = monthly_cancel.sort_values('month_name')
        
        # Plotly line chart
        fig_cancel = px.line(
        monthly_cancel,
        x='month_name',
        y='arr_cancelled',
        markers=True,
        color_discrete_sequence=['#6a040f'],
        labels={'month_name': 'Month', 'arr_cancelled': 'Cancelled Flights'}
        )

        fig_cancel.update_traces(
            hovertemplate=
            "<b>Month %{x}</b><br>" +  # bold month
            "Cancellations: %{y:,}<extra></extra>"  # comma separator + no extra box
        )

        fig_cancel.update_layout(
            hovermode='x unified',
            showlegend=False,
            # plot_bgcolor='#ffffff',
            # paper_bgcolor='#ffffff',
            xaxis_title=None,
            yaxis_title=None)
        
        st.plotly_chart(fig_cancel, use_container_width=True)


# -------------------- COLUMN 3 --------------------
with col3:
    with st.container(border=True):
        st.subheader("Delays & Cancellations by State (%)")
        #Update: changed from total to percentages (delays + cancellations / total flights per state)
        # Group by state: total delayed flights (15+ min) + cancellations
        if selected_month == 'All':
            df_state_delay_cancel = df_merged[df_merged['year'] == selected_year].copy() #just updated
        else:
            df_state_delay_cancel = df_merged[(df_merged['year'] == selected_year) & (df_merged['month'] == selected_month)].copy()
        df_state_delay_cancel['delay_cancel_total'] = (df_state_delay_cancel['arr_del15'] + df_state_delay_cancel['arr_cancelled'])
        df_state_delay_cancel['total_flights'] = df_state_delay_cancel['arr_flights']


        state_summary = df_state_delay_cancel.groupby('STATE').agg({'delay_cancel_total':'sum','total_flights':'sum'}).reset_index()
        state_summary['pct_affected'] = state_summary['delay_cancel_total']/state_summary['total_flights']

        # Custom color palette 
        custom_colors = ['#590d22', '#800f2f', '#a4133c', '#c9184a', '#ff4d6d', '#ff758f', '#ff8fa3', '#ffccd5'] #dark to light

        # Plot choropleth map
        fig = px.choropleth(
            state_summary,
            locations='STATE',
            locationmode='USA-states',
            color='pct_affected',
            color_continuous_scale=custom_colors,
            scope='usa',
            labels={'pct_affected': '% Affected'}
        )

        fig.update_layout(
            template=None,
            paper_bgcolor='rgba(0,0,0,0)',  # removes white canvas
            plot_bgcolor='rgba(0,0,0,0)',   # removes plot background
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=10, r=10, t=20, b=10),
            height=450,
            coloraxis_colorbar=dict(
                thickness=12,
                len=0.6,
                yanchor="middle",
                y=0.5,
                title='% Affected',
                ticks='outside'
            )
        )
        fig.update_traces(hovertemplate="<b>%{location}</b><br>% Affected: %{z:.2%}<extra></extra>")

        st.plotly_chart(fig, use_container_width=True)
        
    with st.container(border=True):
        st.subheader("Top 10 Airports by Delay + Cancellation (%)")

        # Compute affected ratio per airport
        airport_stats = df_selected.copy()
        airport_stats['affected'] = airport_stats['arr_del15'] + airport_stats['arr_cancelled']

        airport_grouped = (
            airport_stats.groupby('airport')[['arr_flights', 'affected']]
            .sum()
            .reset_index()
        )

        airport_grouped['pct_affected'] = airport_grouped['affected'] / airport_grouped['arr_flights']
        airport_grouped = airport_grouped.dropna()
        airport_top10 = airport_grouped.sort_values(by='pct_affected', ascending=False).head(10)

        # Sort for clean bar order
        airport_top10 = airport_top10.sort_values('pct_affected', ascending=True)

        # Plot
        fig_airports = px.bar(
        airport_top10,
        x='pct_affected',
        y='airport',
        orientation='h',
        color='pct_affected',
        color_continuous_scale=['#ff8fa3','#800f2f'],
        labels={'pct_affected': '% Affected'})

        fig_airports.update_layout(
            xaxis_tickformat='.0%',
            # plot_bgcolor='#ffffff',
            # paper_bgcolor='#ffffff',
            coloraxis_showscale=False,
            yaxis=dict(
                title='',
                tickfont=dict(family='Arial Black', size=13), 
                color='black'
            ),
            xaxis=dict(title=''),
            height=450
        )

        fig_airports.update_traces(
            hovertemplate='%{y}<br>Percent Affected: %{x:.2%}<extra></extra>')

        st.plotly_chart(fig_airports, use_container_width=True)
