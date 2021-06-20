import matplotlib.pyplot as plt
plt.figure(figsize = (10, 5))
#ax = fig.add_axes([0,0,1,1])
values = ['Sem clientes', 'Sem jogar', 'Jogando']
data = [0, 21771, 36418] 
data = [0, 16762, 31320] 
plt.bar(values, data,  color = 'green', width=0.4)
#ax.bar(values ,data)
plt.ylabel("Uso em Bytes")
plt.xlabel("Teste feito")
plt.savefig('grafico.png')
