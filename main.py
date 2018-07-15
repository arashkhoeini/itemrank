from ItemRank import ItemRank
import numpy as np

#Testing code with MovieLens 100k dataset
USER_SIZE = 943

#Rading train and test data
with open("u1.base") as file:
	data = []
	for line in file:
		data.extend(line.rstrip("\n").split("\t"))
np_data = np.array(data).reshape(-1,4).astype(int)
with open("u1.test") as file:
	data = []
	for line in file:
		data.extend(line.rstrip("\n").split("\t"))
np_test_data = np.array(data).reshape(-1,4).astype(int)

#training and testing the model
item_rank = ItemRank(np_data)
item_rank.generate_graph()
item_rank.generate_coef_from_graph()
DOAs = []
for user_name in range(1,USER_SIZE+1):
    d = item_rank.generate_d(user_name=user_name)
    IR = np.ones(len(item_rank.movie_names))
    old_IR = IR
    converged = False
    counter = 0
    while not converged:
    	counter += 1
    	old_IR = IR
    	IR = item_rank.item_rank(0.85 , IR , d)
    	converged = (old_IR - IR < 0.0001).all()
    print "Converged after "+str(counter)+" counts."
    doa = item_rank.calculate_DOA(np_test_data, user_name , IR)
    DOAs.append(doa)
    print "DOA for user %s is : %s" %(user_name, doa)
print "Macro DOA: %s" %sum(DOAs)/len(DOAs)
