from __future__ import division
import numpy as np 

class Node(object):
	def __init__(self):
		self.neighbours = []

class ItemRank(object):
	def __init__(self, np_data):
		self.movie_names = []
		self.user_names = []
		self.movie_nodes = {}
		self.user_nodes = {}
		self.data = np_data



	def generate_graph(self):
		node = Node();
		self.movie_names = list(set(self.data[:,1]))
		self.user_names = list(set(self.data[:,0]))
		self.movie_nodes = {}
		self.user_nodes = {}
		for movie in self.movie_names:
			node = Node()
			node.name = movie
			self.movie_nodes[movie] = node
		for user in self.user_names:
			node = Node()
			node.name = user
			self.user_nodes[user] = node
		for i in range(len(self.data[:,0])):
			self.user_nodes[self.data[i,0]].neighbours.append(self.movie_nodes[self.data[i,1]])
			self.movie_nodes[self.data[i,1]].neighbours.append(self.user_nodes[self.data[i,0]])


	def generate_coef_from_graph(self):
		correlation_matrix = np.zeros((len(self.movie_names) , len(self.movie_names)))
		for movie_name in self.movie_nodes.keys():
			for user in self.movie_nodes[movie_name].neighbours:
				for movie in user.neighbours:
					if movie != self.movie_nodes[movie_name]:
						correlation_matrix[self.movie_names.index(movie_name) , self.movie_names.index(movie.name)] +=1
		for c in range(len(correlation_matrix[1,:])):
			correlation_matrix[:,c] /= sum(correlation_matrix[:,c])

		self.correlation_matrix =  correlation_matrix

	def item_rank(self, alpha, IR, d):
		return alpha * np.dot(self.correlation_matrix, IR) + (1-alpha) * d

	def generate_d(self, user_name):
		d = np.zeros(len(self.movie_names))
		for i in range(len(self.data[:,0])):
			if self.data[i,0] == user_name:
				d[self.movie_names.index(self.data[i,1])] = self.data[i,2]
		return d

	def calculate_DOA(self, np_test_data, user_name , IR):
		Tu = self.calculate_Tu(np_test_data,user_name)
		NW = self.calculate_NW_for_user(np_test_data,user_name)
		s = 0
		for movie1 in Tu:
			for movie2 in NW:
				s += self.check_order(IR,movie1, movie2)
		return s / (len(Tu)*len(NW))



	def calculate_NW_for_user(self,np_test_data, user_name):
		NW = set()
		all_data = np.concatenate((np_data, np_test_data), axis = 0)
		user_rated_movies = []
		for i in range(len(all_data[:,0])):
			if all_data[i,0] == user_name:
				user_rated_movies.append(all_data[i,1])
		for j in range(len(all_data[:,0])):
			if all_data[j,1] not in user_rated_movies:
				NW.add(all_data[j,1])
		return list(NW)

	def calculate_Tu(self,np_test_data, user_name):
		Tu = set()
		for i in range(len(np_test_data[:,0])):
			if np_test_data[i,0] == user_name:
				Tu.add(np_test_data[i,1])
		return list(Tu)
		
	def check_order(self, IR, j , k ):
		try:
			if IR[self.movie_names.index(j)] >= IR[self.movie_names.index(k)]:
				return 1
			else:
				return 0
		except ValueError:
			print "ValueError"
			return 1




def generate_correlation_matrix(np_data):
	movies = list(set(np_data[:,1]))
	users = list(set(np_data[:,0]))
	correlation_matrix = np.zeros((len(movies) , len(movies)))
	for i in range(len(movies)):
		for j in range(len(movies)):
			for k in range(len(np_data[:,0])):
				for l in range(len(np_data[:,0])):
					if np_data[k,0] == np_data[l,0]:
						 if np_data[k,1] != np_data[l,1]:
						 	correlation_matrix[movies.index(np_data[k,1]),movies.index(np_data[l,1])] += 1
	return correlation_matrix/(len(movies)*len(movies))



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
#print np_data

fake_data = np.array([
	[1 , 1 , 2]
	,[1, 2 , 3]
	,[1 ,3 , 5]
	,[1 ,4 , 5]
	,[2 ,3 , 4]
	,[2 , 4 , 4]
	,[2 , 1 , 3]
	,[3 , 2 , 5]
	,[3, 3 , 3]
	,[4 , 1 , 4]
	,[4, 3, 4]
	,[4 , 4 , 3]
	,[4 ,2 , 5]])
item_rank = ItemRank(np_data)
item_rank.generate_graph()
item_rank.generate_coef_from_graph()
d = item_rank.generate_d(user_name=1)
IR = np.ones(len(item_rank.movie_names))
IR = d
old_IR = IR
converged = False
counter = 0
while not converged:
	counter += 1
	old_IR = IR
	IR = item_rank.item_rank(0.85 , IR , d)
	converged = (old_IR - IR < 0.0001).all()
print "Converged after "+str(counter)+" counts."
print "DOA : "+ str(item_rank.calculate_DOA(np_test_data,1 , IR)) 
