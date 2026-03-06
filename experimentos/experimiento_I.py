import pandas as pd

if __name__ == "__main__":
    #Importamos datos del experimento I
    data = pd.read_csv('C:\\Users\\lenovo\\Documents\\Daniel\\MISW\\semestre_IV\\MISW4501\\proyecto\\TravelHub-ProyectoFinal\\experimentos\\table.csv', encoding =  'utf-8')
    
    #Sacamos el percentil 95
    data['Latency'] = data['Latency'].astype(float)
    percentile_95 = data['Latency'].quantile(0.95)
    print(f"El percentil 95 de la latencia es: {percentile_95} ms")