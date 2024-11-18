import streamlit as st
import pandas as pd
import plotly.express as px

# Título do Webapp
st.title("Analisador de Consumo de Energia Residencial")
st.write("Faça upload do seu arquivo CSV para analisar o consumo de energia.")

# Upload do arquivo CSV
arquivo = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if arquivo:
    # Ler o arquivo CSV
    df = pd.read_csv(arquivo)

    # Validar se o arquivo tem as colunas esperadas
    colunas_esperadas = ['Data/Hora', 'Consumo em kWh', 'Custo Total']
    if not all(coluna in df.columns for coluna in colunas_esperadas):
        st.error(f"O arquivo deve conter as colunas: {', '.join(colunas_esperadas)}")
    else:
        st.success("Arquivo validado com sucesso!")

        # Exibir as primeiras linhas do dataset para validação
        st.write("Primeiras linhas do arquivo:")
        st.dataframe(df.head())

        # Converter a coluna "Data/Hora" para o formato datetime
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])

        # Criar colunas adicionais para análise
        df['Dia'] = df['Data/Hora'].dt.date
        df['Hora'] = df['Data/Hora'].dt.hour

        # Calcular o consumo total por dia
        consumo_diario = df.groupby('Dia')['Consumo em kWh'].sum().reset_index()

        # Criar o gráfico
        fig_diario = px.bar(consumo_diario, x='Dia', y='Consumo em kWh',
                            title="Consumo Total por Dia",
                            labels={'Consumo em kWh': 'Consumo (kWh)', 'Dia': 'Data'})

        # Mostrar o gráfico no app
        st.plotly_chart(fig_diario)

        # Calcular o consumo médio por hora
        consumo_horario = df.groupby('Hora')['Consumo em kWh'].mean().reset_index()

        # Criar o gráfico
        fig_horario = px.line(consumo_horario, x='Hora', y='Consumo em kWh',
                              title="Consumo Médio por Hora do Dia",
                              labels={'Consumo em kWh': 'Consumo Médio (kWh)', 'Hora': 'Hora'})

        # Mostrar o gráfico no app
        st.plotly_chart(fig_horario)


        # Categorizar os horários
        def categorizar_horario(hora):
            if 18 <= hora <= 22:
                return "Pico"
            elif 22 <= hora or hora < 6:
                return "Noturno"
            else:
                return "Diurno"


        df['Categoria'] = df['Hora'].apply(categorizar_horario)

        # Calcular o consumo por categoria
        consumo_categoria = df.groupby('Categoria')['Consumo em kWh'].sum().reset_index()

        # Criar o gráfico de pizza
        fig_categoria = px.pie(consumo_categoria, values='Consumo em kWh', names='Categoria',
                               title="Distribuição do Consumo por Categoria")

        # Mostrar o gráfico no app
        st.plotly_chart(fig_categoria)

        # Filtros de data
        data_inicio, data_fim = st.sidebar.date_input(
            "Selecione o período:",
            [df['Dia'].min(), df['Dia'].max()]
        )

        # Aplicar o filtro
        df_filtrado = df[(df['Dia'] >= pd.to_datetime(data_inicio)) & (df['Dia'] <= pd.to_datetime(data_fim))]

        # Mostrar informações do período filtrado
        st.write(f"Consumo total no período: {df_filtrado['Consumo em kWh'].sum():.2f} kWh")
        st.write(f"Custo total no período: R$ {df_filtrado['Custo Total'].sum():.2f}")
else:
    st.warning("Por favor, carregue um arquivo CSV para continuar.")
