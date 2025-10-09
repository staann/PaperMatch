import pandas as pd
import numpy as np
import random

pesos = np.random.rand(2)

pesos_normalizados = pesos/np.sum(pesos)

print(np.sum(pesos))

#pesos_normalizados = pesos/(pesos[0]+pesos[1])
print(pesos_normalizados)