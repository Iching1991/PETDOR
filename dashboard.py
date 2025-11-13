# dashboard.py
import pandas as pd
import matplotlib.pyplot as plt
from db import conectar

conn = conectar()


def get_user_history(usuario_id):
df = pd.read_sql_query('SELECT id, pet_nome, especie, percentual, data_avaliacao FROM avaliacoes WHERE usuario_id = ? ORDER BY data_avaliacao DESC', conn, params=(usuario_id,))
if not df.empty:
df['data_avaliacao'] = pd.to_datetime(df['data_avaliacao'])
return df


def show_history_and_plot(usuario_id):
df = get_user_history(usuario_id)
if df.empty:
return False
st.dataframe(df.rename(columns={'data_avaliacao':'Data','pet_nome':'Pet','especie':'Espécie','percentual':'Percentual'}), use_container_width=True)
df_plot = df.sort_values('data_avaliacao')
plt.figure(figsize=(8,4))
plt.plot(df_plot['data_avaliacao'], df_plot['percentual'], marker='o')
plt.title('Percentual estimado de dor')
plt.xlabel('Data')
plt.ylabel('Percentual (%)')
plt.tight_layout()
st.pyplot(plt)
plt.clf()
return True
