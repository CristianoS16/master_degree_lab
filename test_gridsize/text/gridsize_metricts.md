<details>

<summary>Número de nós</summary>

* Fakenews mantem a consistência conforme o grid size aumenta. O grupo `True` sempre esta abaixo do grupo `Fake`.
* No DPOC ocorre uma inversão, o grupo `Bottom` começa superior, com uma diferença de mais de 10%. Conforme o grid size aumenta os grupos se invertem e o grupo `Top` fica superior, com uma diferença de quase 8%.
* No IAM um efeito semelhante é obsevado, `Bottom` superior no inicio, com diferença próxima a 10%. No final se inverte, com diferença próxima a 2%.

### Fakenews
![alt text](image.png)

### DOPC
![alt text](image-2.png)

### IAM
![alt text](image-3.png)

</details>

<details>

<summary>Número de arestas</summary>

* Fakenews parece ocorrer uma saturação, inicialmente começa com o `Fake` maior, mas conforme os grid size aumentar os dois valores convergem para um máximo, 120.
* DPOC, inicia com o grupo `Top` maior, conforme o grid size aumenta os valores entre os grupos vão se aproximando. Provavelmente não terminaram com valores iguais por não ter atigindo a saturação.
* IAM ocorre o mesmo efeito anterior, `Top` comeca superior, valores se apróximas mas não terminam iguais.

### Fakenews
![alt text](image-4.png)

### DOPC
![alt text](image-6.png)

### IAM
![alt text](image-5.png)

</details>




<details>
<summary>Distancia Media</summary>

* Fakenews permanece consistente apesar da distancia entre os valores estreitar no meio da variação, principalmente para o grid size de 20
* DPOC há uma inversão logo no inicio da variação, inicialmente os valores estão próximos com o `Top` superior mas na primeira iteração os grupos já invertem.
* IAM exatamente o mesmo comportamento anterior, na primeira iteração ocorre a inversão.

### Fakenews
![alt text](image-7.png)

### DOPC
![alt text](image-8.png)

### IAM
![alt text](image-9.png)


</details>


<details>
<summary>Diametro</summary>

* Fakenews Ocorre inversão dos valores, `Fake` começa superior e terminar inferior.
* DPOC ocorre uma inversão muito notoria, grupo `Top` começa com valor muito superior e temrinar com valor muito inferior.
* IAM replica o mesmo comportamento anterior

### Fakenews
![alt text](image-10.png)

### DOPC
![alt text](image-11.png)

### IAM
![alt text](image-12.png)

</details>


<details>
<summary>Beetweenness</summary>

* Fakenews ocorre inversão logo na primeira iteração, mas valores são baixos.
* DPOC é consistente ao longo de todos os valores de grid size, valor `Top` é superior mas para o ginal os valores se apróximam muito.
* IAM replica o mesmo comportamento do DPOC

### Fakenews
![alt text](image-13.png)

### DOPC
![alt text](image-14.png)

### IAM
![alt text](image-15.png)

</details>

<details>
<summary>Grau Médio</summary>

* Fakenews, valores bem próximos em todos os casos, sendo iguais a partir do grid size 30. Ocorre uma inversão que pode ser desconsiderada.
* DPOC `Top` comeca supeiror e podesse dizer que valores terminam empatados... Grupo `Bottom` vai crescendo até chegar ao mesmo valor do `Top`.
* IAM apresenta o mesmo efeito dp DPOC

### Fakenews
![alt text](image-16.png)

### DOPC
![alt text](image-17.png)

### IAM
![alt text](image-18.png)

</details>

<details>
<summary>Força do nó</summary>

* Fakenews Valores são iguais em praticamente todas as ocorrencias.
* DPOC Apesar do grupo `Top` começar consideravelmente superior, há uma leve inversão para valores elevados de grid size.
* IAM mesmo efeito do PDOC.

### Fakenews
![alt text](image-19.png)

### DOPC
![alt text](image-20.png)

### IAM
![alt text](image-28.png)

</details>

<details>
<summary>Assortatividade</summary>

* Fakenews consistente com o grupo `Fake` sempre inferior. Mas é interessante que passa de valores positivos de assortatividade para valores negativos.
* DPOC Consistente com o grupo `Top` sempre apresentado valores inferiores, sempre muito proximo a zero.
* IAM consistente com o top sempre inferior mas com valores de assortatividade sempre positivos.

### Fakenews
![alt text](image-22.png)

### DOPC
![alt text](image-23.png)

### IAM
![alt text](image-24.png)

</details>

<details>
<summary>Centro de Massa</summary>

* Fakenews inicialente `Fake` apresenta resultado superior, valores sempre muito proximos e terminam iguais.
* DPOC começá com grupo Bottom muito superior e terminar invertido.
* IAM não ocorre inversão, grupo bottom sempre esta superior mas tente a se aproximar conforme o grid size aumenta.

### Fakenews
![alt text](image-25.png)

### DOPC
![alt text](image-26.png)

### IAM
![alt text](image-27.png)

</details>
