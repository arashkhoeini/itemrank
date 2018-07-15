from __future__ import division
import numpy as np

class Node(object):
	"""
		This class is used to generate a graph of users and items. That graph
		will be mainly used to generate a coefficient matrix.
	"""
	def __init__(self):
		self.neighbours = []

class ItemRank(object):
	"""
		This class contains methods to implement ItemRank algorithm. sample use
		of this class is as below:
		 item_rank = ItemRank(data)

	"""

	#data must be in a format of move,item,rate
	def __init__(self, np_data):
		self.movie_names = []
		self.user_names = []
		self.movie_nodes = {}
		self.user_nodes = {}
		self.data = np_data


	#generates bipartial user/item graph.
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
	#generates d, which is a vector of user rates to all movies
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
		all_data = np.concatenate((self.data, np_test_data), axis = 0)
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
			return 1
