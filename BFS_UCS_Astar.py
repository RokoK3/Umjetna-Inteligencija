import sys
from queue import PriorityQueue
from collections import deque

#BFS algoritam koji koristim je napisan uz pomoć pseudokoda danog u prezentaciji sa predavanja, u njega sam još dodao
#stvari potrebne za zadatak kao što su rekreacija patha uz pomoć roditelja svakog nodea, set u kojem cuvam posjecena stanja
#kako bih optimizirao algoritam i još imam brojac posjecenih čvorova

def BFS(s0, succ, goal_states):
    open = deque([(s0, None)])  # u deque open dodaj pocetno stanje, njegov roditelj je None
    open_set = set([s0]) #u open set drzim stanja koja su u open, u setu lakse trazim jel sadrzan neki element
    visited = set() #za posjecena stanja set
    parent = {s0 : None}  # dictionary roditelja
    visited_count = 0 #broj posjecenih nodeova

    while len(open) != 0: #dok ima necega u open dequeu
        current_node, parent_node = open.popleft()  # uzmi najlijevijeg i njegovog roditelja
        visited_count += 1 #povecaj broj posjecenih nodeova
        if current_node in goal_states: #ako je n zeljeno stanje
            path = [current_node] #u listi path rekreiram put, dodaj ciljni node 
            while parent_node is not None: # parent ce biti None kada dodem do inicijalnog cvora, njegov roditelj je None
                path.append(parent_node) #dodaj parenta u path
                parent_node = parent[parent_node] # trazi roditelja od roditelja
            path.reverse() #obrni ga jer smo ga dobili od dna prema vrhu
            return path, visited_count #vracam path i broj posjecenih stanja
        
        visited.add(current_node) #dodaj ga u posjecene

        for child_node in sorted(succ[current_node]): #za svaki child_node koji je nasljednik trenutnog nodea poredanih abecedno
            if child_node not in visited and child_node not in open_set: #ako child_node vec nije posjecen i nije u redu za cekanje da bude prosiren
                open.append((child_node, current_node))  # dodaj u listu open child_node i njegovog roditelja current_node
                open_set.add(child_node) # u open set dodaj child_node 
                parent[child_node] = current_node  #zabiljezi da je roditelj od child_nodea current_node
    return False # False ako nismo dosli do konacnog stanja

#UCS algoritam napisan je vrlo slično kao i BFS. Razlika je u tome što je trenutni red čekanja implementiran kao priority
#queue u kojem će najlijeviji element imati najmanju cijenu puta. Osim toga, parent dictionary čuva cijenu puta pređenog
#do sebe, time provjeravam ima li child node jeftiniji put od trenutno najjeftinijeg. Open_set mi drži sve nodeove koji
#se nalaze u priority queueu, a služi kao efikasan način provjere je li neki trenutni node u priority queueu
def UCS(s0, succ, goal_states):
    open = PriorityQueue() #priority queue koji ce drzati poredak cvorova tako da je najjeftiniji prvi
    open.put((0, s0, None)) #drzim u njemu redom cijenu, ime stanja, roditelj stanja
    visited = set() #vec posjeceni cvorovi, za efikasnost
    parent = {s0: (None, 0)} #roditelj pocetnog stanja je None, a cijena je 0
    open_set = set([s0]) #set u kojem cu drzati stanja koja su u prioq, za efikasnost
    visited_count = 0 #broj posjecenih nodeova

    while not open.empty(): #dok ima cvorova u open prioq
        current_cost, current_node, parent_node = open.get()  #dohvati trenutnu cijenu, trenutni cvor i roditelja
        visited_count += 1 #povecaj broj posjecenih nodeova
        if current_node in goal_states: #ako je trenutni node prihvatljiv
            path = [current_node] #rekreiraj path pocevsi od zadnjeg stanja
            while parent_node is not None: #parent node je None kada dodem do pocetnog stanja
                path.append(parent_node)
                parent_node, _ = parent[parent_node]
            path.reverse()
            return path, visited_count #vrati path i broj posjecenih stanja

        if current_node in open_set: #ako je trenutni node u open setu makni ga posto smo ga izvukli iz priority queua
            open_set.remove(current_node) #ako nademo jeftiniji put da mozemo dodati novi node u open_set 
        
        visited.add(current_node) #dodaj ga u posjecene

        for child_node, child_node_cost in succ[current_node].items(): #za svaki novi node i njegov pripadajuci cost
            total_cost = current_cost + child_node_cost #total cost izracunaj kao trenutni cost + novi cost
            if child_node not in open_set and child_node not in visited: #ako novi node nije vec u redu za cekanje i nije jos obiden
                open.put((total_cost, child_node, current_node)) #dodaj ga u prioq
                open_set.add(child_node) # azuriraj open_set da prati sve koji su u prioq
                parent[child_node] = (current_node, total_cost) #zabiljezi roditelja novog nodea i cijenu puta do njega
            elif (child_node in open_set or child_node in visited) and total_cost < parent[child_node][1]:#ako je novi node u redu za cekanje, ali smo nasli povoljniji put
                open.put((total_cost, child_node, current_node)) #dodaj ga u prioq
                open_set.add(child_node) # azuriraj open_set da prati sve koji su u prioq
                parent[child_node] = (current_node, total_cost) #zabiljezi roditelja novog nodea i cijenu puta do njega
    return False

#AStar algoritam takoder je napisan uz pomoc pseudokoda iz prezentacije. Kao i ostali algoritmi koje sam implementirao,
#obogacan je mogucnoscu da vraca path uz pomoc roditeljskih cvorova te da vraca broj posjecenih cvorova. Kao i drugi algoritmi,
#koristim visited i open_set setove kako bih ubrzao i optimizirao izvodenje koda.
def AStar(s0, succ, goal_states, h):
    open = PriorityQueue() #prio queue koji na temelju vrijednosti f(put+heuristika) drzi cvorove u redu
    open.put((h[s0], s0, None, 0))#dodaj pocetni node, njgovu heuristiku, ime, roditelja i g vrijednost
    visited = set() # set za posjecena stanja
    parent = {s0: (None, 0)}  #roditelj pocetnog stanja je None, a cijena je 0
    open_set = set([s0]) #set u kojem cu drzati stanja koja su u prioq, za efikasnost
    visited_count = 0 #broj posjecenih cvorova

    while not open.empty(): #dok prioq nije prazan
        _, current_node, parent_node, g = open.get() #uzmi najlijeviji cvor iz open
        visited_count += 1
        if current_node in goal_states: #ako je trenutni cvor zavrsni, generiraj path isto kao i u prosla dva algoritma
            path = [current_node]
            while parent_node is not None:
                path.append(parent_node)
                parent_node, _ = parent[parent_node]
            path.reverse()
            return path, visited_count

        visited.add(current_node) #dodaj trenutni node set visited
        for child_node, child_node_cost in succ[current_node].items(): #za sve successore trenutnog nodea
            g_total_cost = g + child_node_cost #izracunaj g total (cijena puta)
            if child_node in open_set or child_node in visited: #ako je child ili u visited ili u open
                if g_total_cost > parent[child_node][1]: #ako je novi put skuplji od onog koji vec imamo
                    continue #nastavi na iduce dijete
                else: #inace obrisi taj node iz visited i open
                    if child_node in open_set:
                        for node in open.queue:
                            if child_node == node[1]:
                                open.queue.remove(node) #prvo ga micem iz priority queua
                                break
                        open_set.remove(child_node) #pa iz seta koji prati stanje prioqa
                    if child_node in visited: #makni iz visited
                        visited.remove(child_node)

            f_value = g_total_cost + h[child_node] #izracunaj vrijednost f
            open.put((f_value, child_node, current_node, g_total_cost))#dodaj u prioq novi node sa vrijednosti f_value
            open_set.add(child_node)#dodaj u set open_set da pratim stanje prioqa
            parent[child_node] = (current_node, g_total_cost) #zabiljezi roditelja djeteta
    return False


alg = "" #ime algoritma
ss = "" #opisnik stanja
h = "" #opisnik heuristike
check_optimistic = False #provjeravam li optimistiku
check_consistent = False #provjeravam li konzistentnost
arglen = len(sys.argv) #broj argumenata pri pozivu programa
index = 1 #kreni od 1 jer je 0 ime programa
while index < arglen: #gledaj koje argumente smo dobili, na njihovom indexu+1 se nalazi ime datoteke ili algoritma
    if sys.argv[index] == "--alg":
        index += 1
        alg = sys.argv[index]
    elif sys.argv[index] == "--ss":
        index += 1
        ss = sys.argv[index]
    elif sys.argv[index] == "--h":
        index += 1
        h = sys.argv[index]
    elif sys.argv[index] == "--check-optimistic":
        check_optimistic = True
    elif sys.argv[index] == "--check-consistent":
        check_consistent = True
    index += 1

if ss != "":
    state_space = {} #dict za opisnik stanja
    initial_state = "" #pocetno stanje
    goal_states = set() #prihvatljiva stanja
    with open(ss, 'r') as state_file:
        lines = state_file.readlines() #svi retci iz datoteke

    for line in lines:
        line = line.strip()

        if line.startswith("#"): #komentar linija
            continue

        if initial_state == "": #ako jos nije postavljeno
            initial_state = line
            continue

        if len(goal_states) == 0: #ako ih jos nema
            goal_states = set(line.split())
            continue

        state, transitions = line.split(":") #podijeli liniju na trenutno stanje i njegove prijelaze
        transitions_list = transitions.split() # odijeli tranzicije izmedu kojih je razmak

        transitions_dict = {}
        for trans in transitions_list:
            next_state, cost = trans.split(",") #iduce stanje i cijena su odijeljeni razmakom
            transitions_dict[next_state] = float(cost) #u dictionary tranzicija drzi {iduce stanje : cijena}

        state_space[state] = transitions_dict #u dictionary opisnika prostora drzi {stanje : {iduce stanje : cijena}}

if  h != "":
    heuristic_dict = {}

    with open(h, 'r') as heuristic:
        lines = heuristic.readlines() #svi retci heuristic datoteke

    for line in lines:
        line = line.strip()
        if line.startswith("#"): #komentar linija
            continue
        state, heuristic_value = line.split(":") #podijeli s obzirom na :
        heuristic_dict[state] = float(heuristic_value) # heuristic dict {stanje : heuristika}

if alg == "bfs":
    path, len_visited_states = BFS(initial_state, state_space, goal_states) #vrati putanju i broj posjecenih stanja
    if path == False: #ako nema putanje
        print("# BFS")
        print("[FOUND_SOLUTION]: no")
    else:
        print("# BFS")
        print("[FOUND_SOLUTION]: yes")
        print("[STATES_VISITED]: " + str(len_visited_states))
        len_path = len(path) # duljina pronadenog puta
        print("[PATH_LENGTH]: " + str(len_path))
        total_cost = 0 #cijena puta
        for index in range(len_path-1):
            from_state = path[index] #stanje iz kojeg idemo
            to_state = path[index+1] #stanje u koje dolazimo
            total_cost += state_space[from_state][to_state] #cijena tog prijelaza
        print("[TOTAL_COST]: " + str(total_cost))
        print("[PATH]: " + " => ".join(path)) #odijeli sa =>

if alg == "ucs":
    path, len_visited_states = UCS(initial_state, state_space, goal_states)
    if path == False:
        print("# UCS")
        print("[FOUND_SOLUTION]: no")
    else:
        print("# UCS")
        print("[FOUND_SOLUTION]: yes")
        print("[STATES_VISITED]: " + str(len_visited_states))
        len_path = len(path) # duljina pronadenog puta
        print("[PATH_LENGTH]: " + str(len_path))
        total_cost = 0
        for index in range(len_path-1):
            from_state = path[index] #stanje iz kojeg idemo
            to_state = path[index+1]  #stanje u koje dolazimo
            total_cost += state_space[from_state][to_state]  #cijena tog prijelaza
        print("[TOTAL_COST]: " + str(total_cost))
        print("[PATH]: " + " => ".join(path)) #odijeli sa =>

if alg == "astar":
    path, len_visited_states = AStar(initial_state, state_space, goal_states, heuristic_dict)
    if path == False:
        print("# A-STAR " + h)
        print("[FOUND_SOLUTION]: no")
    else:
        print("# A-STAR " + h)
        print("[FOUND_SOLUTION]: yes")
        print("[STATES_VISITED]: " + str(len_visited_states))
        len_path = len(path)
        print("[PATH_LENGTH]: " + str(len_path))  # duljina pronadenog puta
        total_cost = 0
        for index in range(len_path-1):
            from_state = path[index] #stanje iz kojeg idemo
            to_state = path[index+1] #stanje u koje dolazimo
            total_cost += state_space[from_state][to_state]  #cijena tog prijelaza
        print("[TOTAL_COST]: " + str(total_cost))
        print("[PATH]: " + " => ".join(path))

if check_optimistic:
    isOptimistic = True
    print("# HEURISTIC-OPTIMISTIC " + h)
    for state in state_space: #za svako moguce stanje
        path, visited_states = UCS(state, state_space, goal_states) #pokreni ucs u kojem je to stanje pocetno stanje
        if path: #ako ima put do zavrsnog stanja
            total_cost = 0.0 #izracunaj cost koji da ucs
            len_path = len(path)
            for index in range(len_path-1):
                from_state = path[index]
                to_state = path[index+1]
                total_cost += state_space[from_state][to_state]
            heuristic_approx = heuristic_dict[state] # cijena koju da heuristika
            if heuristic_approx > total_cost: #ako je heuristika skuplja od UCSa onda nije optimisticna
                isOptimistic = False
                print("[CONDITION]: [ERR] h("+state+") <= h*: "+ str(heuristic_approx) + " <= " + str(total_cost))
            else:
                print("[CONDITION]: [OK] h("+state+") <= h*: "+ str(heuristic_approx) + " <= " + str(total_cost))
    if not isOptimistic:
        print("[CONCLUSION]: Heuristic is not optimistic.")
    else:
        print("[CONCLUSION]: Heuristic is optimistic.")

if check_consistent:
    isConsistent = True
    print("# HEURISTIC-CONSISTENT " + h)
    for from_state in state_space: #stanje iz kojeg idemo
        for to_state in state_space: #stanje u koje dolazimo

            if to_state in state_space[from_state]: #ako se iz pocetnog moze doci u zavrsno stanje
                c = state_space[from_state][to_state] #izracunaj cost tog prijelaza
            else:
                continue #inace nastavi na drugo stanje

            h1 = heuristic_dict[from_state] #heuristika stanja iz kojeg se ide
            h2 = heuristic_dict[to_state] #heuristika stanja u koje se ide

            if h1 <= h2 + c: #ako je heuristika stanja iz kojeg se ide manje jednaka cijeni heuristike u koju se dolazi plus cijena prijelaza
                print("[CONDITION]: [OK] h("+from_state+") <= h(" + to_state + ") + c: " + str(h1) + " <= " + str(h2) + " + " + str(c))
            else:
                print("[CONDITION]: [ERR] h("+from_state+") <= h(" + to_state + ") + c: " + str(h1) + " <= " + str(h2) + " + " + str(c))
                isConsistent = False    
    if not isConsistent:
        print("[CONCLUSION]: Heuristic is not consistent.")
    else:
        print("[CONCLUSION]: Heuristic is consistent.")