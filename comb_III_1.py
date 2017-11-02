class GraphError(Exception): pass

class NamedEdgesList:
    
    def __init__(self):
        self.__edges = []    #[weight, begin, end]
        self.__tops = []
        
    def __exist(self, top):
        return top in self.__tops

    def addIfNotExist(self, top):
        if not self.__exist(top):
            self.__tops.append(top)
        
    def addEdge(self, top1, top2, weight=1):
        self.addIfNotExist(top1)
        self.addIfNotExist(top2)
        if [weight, top2, top1] not in self.__edges:
            self.__edges.append([weight, top1, top2])
            
    def removeEdge(self, edge):
        self.__edges.remove(edge)
        
    def getAdjacent(self, top):
        if not self.__exist(top):
            return
        adj = []
        for i in self.__edges:
            if top in i:
                i = i[:]
                i.remove(top)
                adj.append(i[1])
        return adj
        
    def getTops(self):
        return self.__tops
    
    def getEdges(self):
        return self.__edges


class Graph:
    
    def __init__(self, tops_type):
        self.__type = tops_type
        self.__edges = NamedEdgesList()

    def add(self, top):
        try:
            self.__edges.addIfNotExist(self.__type(top))
        except TypeError:
            raise GraphError('Вершина должна быть типа', self.__type)
        
    def addEdge(self, top1, top2, weightComputer):
        self.__edges.addEdge(top1, top2, weightComputer(top1, top2))
        
    def removeEdge(self, edge):
        self.__edges.removeEdge(edge)
        
    def makeFull(self, weights):
        self.tops = self.__edges.getTops()
        for top1 in self.tops:
            for top2 in self.tops:
                if top1 != top2:
                    self.addEdge(top1, top2, weights)
            
    def getTops(self):
        return self.__edges.getTops()
        
    def getEdges(self):
        return self.__edges.getEdges()
        
    def getAdjacent(self, top):
        return self.__edges.getAdjacent(top)
        
class DisjointSetUnion:
    
    def __init__(self, items):
        self.parents = {i:i for i in items}
        
    def findSet(self, itm):
        if self.parents[itm] == itm:
            return itm
        self.parents[itm] = self.findSet(self.parents[itm])
        return self.parents[itm]

    def unionSets(self, itm1, itm2):
        itm1 = self.findSet(itm1)
        itm2 = self.findSet(itm2)
        if itm1 != itm2:
            allParents = list(self.parents.values())
            if allParents.count(itm1) >= allParents.count(itm2):
                self.parents[itm2] = itm1
            else:
                self.parents[itm1] = itm2
            return True
        return False
        
        
def metrics(p1, p2):
    p1_x, p1_y, p2_x, p2_y = map(lambda a: int(a), p1.split(' ')+p2.split(' '))
    return abs(p1_x-p2_x) + abs(p1_y-p2_y)

def main():
    with open(r'D:\Programs\Eclipse\projects\sharagen\comb1.txt', 'r') as fi:
        data = fi.read().split('\n')
    graph = Graph(str)
    for i in range(int(data.pop(0))):
        graph.add(data[i])
    graph.makeFull(metrics)
    connComponents = DisjointSetUnion(graph.getTops())
    sortd = sorted(graph.getEdges())
    #print('\n'.join(str(i) for i in sortd))
    maxWeight = 0
    for i in sortd:
        if connComponents.unionSets(i[1], i[2]):
            maxWeight += i[0]
        else:
            graph.removeEdge(i)
    #print('******\n'+'\n'.join(str(i) for i in graph.getEdges()))
    for top in graph.getTops():
        print('%s: %s' % (top, graph.getAdjacent(top)))
    print(maxWeight)

main()