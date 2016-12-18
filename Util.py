import numpy as np
from scipy import linalg
import sklearn.cluster as sc
from sklearn import linear_model
# dataset is A
def test(dataset_path, sigma):
    matrix = get_adjacent_matrix(dataset_path)
    P = find_geodesic_distances(matrix)
    P = np.array(P)
    S = (np.exp(-(P*P)/(2 * sigma ** 2)))
    return S

def find_geodesic_distances(M):
    """
    find_geodesic_distances(M)
    计算点对之间的最短距离

    Parameters
    ----------
    M : array-like
        Input values.

    Returns
    -------
    P : ndarray
        geodesic_distances
    """
    M = np.mat(M)
    D = []
    n = len(M)
    D.append(M)
    for k in range(1, n + 1):
        s = (n, n)
        current = np.mat(np.zeros(s))
        D.append(current)
        previous = D[k - 1]

        previous = previous.getA()
        current = current.getA()

        for i in range(n):
            for j in range(n):
                if previous[i][j] > 0: current[i][j] = previous[i][j]
                if i == j: continue
                value1 = previous[i][k - 1]  # from i to k
                value2 = previous[k - 1][j]  # from k to j

                if value1 != 0 and value2 != 0:  # if there is an edge from i to k and k to j then there is edge from i to j
                    if current[i][j] != 0:
                        current[i][j] = min(current[i][j], value2 + value1)
                    else:  # this means previously there is no edge from i to j
                        current[i][j] = value2 + value1

        D[len(D) - 1] = np.mat(current)
    print("APSP (k=%d):" % k)
    # print_graph(D[len(D) - 1])
    P = D[len(D) - 1]
    P = np.array(P)
    return P

def print_graph(G):
    for row in G:
        print(row)

import networkx as nx
def get_data_from_file(path):
    graph = nx.read_gml(path)
    return graph

def get_adjacent_matrix(path):
    matrix = nx.to_numpy_matrix(get_data_from_file(path))
    return matrix
def find_sim(P, sigma = 1):
    S = np.exp(-(P*P)/(2 * sigma ** 2))
    return S

def find_linear_sparse_code(S):
    n = np.shape(S)[0]
    F = np.zeros([n, n])
    for i in range(n):
        Sh = np.column_stack((S[:, :i], np.zeros([n, 1]), S[:, i + 1:]))
        lasso = linear_model.Lasso(alpha = 0.05, fit_intercept = False)
        lasso.fit(Sh, S[:, i])
        w = lasso.coef_ / sum(lasso.coef_)
        F[i, :] = F[i, :] + w
    max_dig = []
    for i in range(n):
        col = F[i, :]
        max_dig.append([np.max(col)])
    F = F / max_dig
    F = (F + np.transpose(F))/2
    return F

def find_eigen_vectors(F,k):
    ds = [np.sum(row) for row in F]
    D = np.diag(ds)
    Dn = np.power(np.linalg.matrix_power(D,-1),0.5)
    L = np.identity(len(F)) - (Dn.dot(F)).dot(Dn)

    evals, evcts = linalg.eig(L)
    vals = dict (zip(evals, evcts.transpose()))
    keys = sorted(vals.keys())
    E = np.array([vals[i] for i in keys[1:k]]).transpose()
    return E

def kmeans(Es,Ea = None,n_clusters = 2):
    E = Es
    if Ea is not None:
        E = (np.concatenate((Es.T, Ea.T))).T
    if (np.sum(E.imag)) > 0: print('the egin is complex number')
    centroid, labels, inertia = sc.k_means(E.real, n_clusters = n_clusters)
    return centroid, labels, inertia

