#!/usr/bin/env python
# coding: utf-8

# ## Funciones lógicas

# Introducimos condiciones lógicas usando declaraciones IF y CASE, e incorporamos operadores AND, OR y NOT para obtener mayor precisión en las consultas. 

# In[1]:


get_ipython().run_line_magic('load_ext', 'sql')


# In[2]:


get_ipython().run_line_magic('sql', 'mysql://studentuser:studentpw@localhost/dognitiondb')


# In[ ]:


get_ipython().run_line_magic('sql', 'USE dognitiondb')


# In[4]:


get_ipython().run_cell_magic('sql', '', "SELECT created_at, IF(created_at<'2014-06-01','early_user','late_user') AS user_type\nFROM users\nLIMIT 3;")


# Por ejemplo, dado que sabemos que hay user_guids duplicados en la tabla de usuarios, podríamos combinar una subconsulta con una declaración IF para recuperar una lista de user_guids únicos con su clasificación como usuario temprano o tardío (según cuándo fue su primera entrada de usuario) y usar GROUP BY para obtener la cantidad de ellos. 

# In[6]:


get_ipython().run_cell_magic('sql', '', "SELECT IF(cleaned_users.first_account<'2014-06-01','early_user','late_user') AS user_type,\n       COUNT(cleaned_users.first_account)\nFROM (SELECT user_guid, MIN(created_at) AS first_account \n      FROM users\n      GROUP BY user_guid) AS cleaned_users\nGROUP BY user_type;")


# Utilizamos la expresión IF para determinar la cantidad de user_guid únicos que residen en los Estados Unidos (abreviado "US") y fuera de los EE. UU, excluyendo cualquier user_guids o países que tengan valores NULL. 

# In[8]:


get_ipython().run_cell_magic('sql', '', "SELECT IF(cleaned_users.country='US','In US','Outside US') AS user_location, \ncount(cleaned_users.user_guid) AS num_guids \nFROM (SELECT DISTINCT user_guid, country \nFROM users \nWHERE user_guid IS NOT NULL AND country IS NOT NULL) AS cleaned_users\nGROUP BY user_location;")


# Las expresiones IF únicas solo pueden dar como resultado una de dos salidas especificadas, pero se pueden anidar varias expresiones IF para dar como resultado más de dos salidas posibles. Cuando anida expresiones IF, es importante encerrar cada expresión IF, así como toda la expresión IF junta, entre paréntesis.

# Examinamos las entradas contenidas en la categoría de países no estadounidenses. Muchos usuarios están asociados con un país llamado "N/A". "N/A" es una abreviatura de "No aplicable"; no es un nombre de país real, entonces debemos separar estas entradas de la categoría "Fuera de los EE. UU." que hicimos anteriormente. 

# In[9]:


get_ipython().run_cell_magic('sql', '', "SELECT IF(cleaned_users.country='US','In US', \n          IF(cleaned_users.country='N/A','Not Applicable','Outside US')) AS US_user, count(cleaned_users.user_guid)   \nFROM (SELECT DISTINCT user_guid, country \n      FROM users\n      WHERE country IS NOT NULL) AS cleaned_users\nGROUP BY US_user;")


# La función IF no es compatible con todas las plataformas de bases de datos, y algunas escriben la función como IIF en lugar de IF, así que asegúrese de verificar dos veces cómo funciona la función en la plataforma que está utilizando.

# Existe otra forma de usar lógica condicional para generar más de dos grupos, es con la función CASE. El propósito principal de las expresiones CASE es devolver un valor singular basado en una o más pruebas condicionales. Puede pensar en las expresiones CASE como una forma eficiente de escribir un conjunto de declaraciones IF y ELSEIF. Se sigue la siguiente sintaxis:
# 
# CASE
#    
#    WHEN [condition set 1] THEN [result you want when the conditions in set 1 are met]
#    
#    WHEN [condition set 2] THEN [result you want when the conditions in set 2 are met]
#    
#    WHEN [condition set 3] THEN [result you want when the conditions in set 3 are met] 
#    
#    ...(can include as many condition sets as you want)
#    
#    ELSE [result you want none of condition sets are met]
#  
#  END
#  
#  
# Reescribimos la consulta usando la función CASE con esta sintaxis:
# 

# In[10]:


get_ipython().run_cell_magic('sql', '', 'SELECT CASE WHEN cleaned_users.country="US" THEN "In US"\n            WHEN cleaned_users.country="N/A" THEN "Not Applicable"\n            ELSE "Outside US"\n            END AS US_user, count(cleaned_users.user_guid)   \nFROM (SELECT DISTINCT user_guid, country \n      FROM users\n      WHERE country IS NOT NULL) AS cleaned_users\nGROUP BY US_user;')


# Debemos asegúrarnos de incluir la palabra END al final de la expresión y no incluir paréntesis. Las expresiones ELSE son opcionales, si se omite una expresión ELSE, se generarán valores NULL para todas las filas que no cumplan ninguna de las condiciones establecidas explícitamente en la expresión.
# Las expresiones CASE se pueden usar en cualquier parte de una instrucción SQL, incluidas las cláusulas GROUP BY, HAVING y ORDER BY o la lista de columnas SELECT.

# La función CASE se pueden usar para renombrar o revisar valores en una columna. Por ejemplo, generamos 3 columnas: dog_guid, dog_fixed y una tercera columna que dice "neutered" cada vez que hay un 1 en la columna "dog_fixed" de dogs, "not neutered" para un valor de 0, y "NULL" cada vez cuando haya cualquier otro valor.

# In[11]:


get_ipython().run_cell_magic('sql', '', 'SELECT dog_guid, dog_fixed, \nCASE dog_fixed\nWHEN "1" THEN "neutered"\nWHEN "0" THEN "not neutered"\nEND AS neutered\nFROM dogs\nLIMIT 5;')


# También se puede usar sentencias CASE para estandarizar o combinar varios valores en uno.  Generamos las siguientes columnas:  dog_guid, exclude y una tercera columna que dice "exclude_cleaned" que tome valor "exclude" cuando en la columna "exclude" sea de dogs y "mantener" cada vez que hay cualquier otro valor en la columna de exclusión. Limite sus resultados para solucionar problemas.
# 

# In[5]:


get_ipython().run_cell_magic('sql', '', 'SELECT dog_guid, exclude, \nCASE exclude\nWHEN "1" THEN "exclude"\nELSE "keep"\nEND AS exclude_cleaned\nFROM dogs\nLIMIT 5;')


# Las expresiones CASE a menudo necesitan múltiples operadores AND, OR y NOT para describir con precisión las condiciones lógicas que desea imponer a los grupos en sus consultas. El orden en que se incluyen estos operadores en las expresiones lógicas, porque a menos que se incluyan paréntesis, el operador NOT siempre se evalúa antes que un operador AND, y un operador AND siempre se evalúa antes que el operador OR. Es decir, el orden de evaluación es el siguiente: 
#             
#                                     1. NOT
#                                     2. AND
#                                     3. OR
# 
# 
# Obtenemos las filas que cumplen las condiciones 2 y 3, o la condición 1:
# ```sql
# CASE WHEN "condition 1" OR "condition 2" AND "condition 3"...
# ```
# 
# En la siguiente consulta, obtenemos las filas que cumplen las condiciones 1 y 3, o la condición 2:   
# ```sql
# CASE WHEN "condition 3" AND "condition 1" OR "condition 2"...
# ```
#    
# Incluyendo paréntesis para obtner las filas que cumplen la condición 1 o 2, y condición 3:
# ```sql
# CASE WHEN ("condition 1" OR "condition 2") AND "condition 3"...
# ```
# 
# Escribimos una consulta para conformar grupos con condiciones específicas:

# In[5]:


get_ipython().run_cell_magic('sql', '', 'SELECT COUNT(DISTINCT dog_guid), \nCASE WHEN breed_group=\'Sporting\' OR breed_group=\'Herding\' AND exclude!=\'1\' THEN "group 1"\n     ELSE "everything else"\n     END AS groups\nFROM dogs\nGROUP BY groups;')


# In[6]:


get_ipython().run_cell_magic('sql', '', 'SELECT COUNT(DISTINCT dog_guid), \nCASE WHEN exclude!=\'1\' AND breed_group=\'Sporting\' OR breed_group=\'Herding\' THEN "group 1"\n     ELSE "everything else"\n     END AS group_name\nFROM dogs\nGROUP BY group_name;')


# Escribimos una consulta que use la instrucción CASE para informar la cantidad de user_guid únicos asociados con clientes que viven en los Estados Unidos y que se encuentran en los siguientes grupos de estados:
# 
# Grupo 1: Nueva York (abreviado "NY") o Nueva Jersey (abreviado "NJ")
# 
# Grupo 2: Carolina del Norte (abreviado "NC") o Carolina del Sur (abreviado "SC")
# 
# Grupo 3: California (abreviado "CA")
# 
# Grupo 4: todos los demás estados con valores no nulos:

# In[7]:


get_ipython().run_cell_magic('sql', '', 'SELECT COUNT(DISTINCT user_guid), \nCASE \nWHEN (state="NY" OR state="NJ") THEN "Group 1-NY/NJ"\nWHEN (state="NC" OR state="SC") THEN "Group 2-NC/SC"\nWHEN state="CA" THEN "Group 3-CA"\nELSE "Group 4-Other"\nEND AS state_group\nFROM users\nWHERE country="US" AND state IS NOT NULL\nGROUP BY state_group;')


# Escribimos una consulta que nos permita determinar cuántos dog_guids únicos están asociados con perros a los que se les realizó una prueba de ADN y tienen dimensiones de personalidad de "stargazer" o "socialite". 

# In[8]:


get_ipython().run_cell_magic('sql', '', "SELECT COUNT(DISTINCT dog_guid)\nFROM dogs\nWHERE dna_tested=1 AND (dimension='stargazer' OR dimension='socialite');")

