import sys
def print_solution(clause, parent_clauses, printed_clauses, visited_clauses):
    # BASE CASE -> ako klauzula nema roditelje ili je vec posjecena ili je vec ispisana
    if clause not in parent_clauses or clause in visited_clauses or clause in printed_clauses: 
        return
    visited_clauses.add(clause)
    clause1, clause2 = parent_clauses[clause] #izvuci roditelje klauzule iz rjecnika
    print_solution(clause1, parent_clauses, printed_clauses, visited_clauses) #idi u dubinu za prvu
    print_solution(clause2, parent_clauses, printed_clauses, visited_clauses) #idi u dubinu za drugu
    if len(clause) == 0:  # Klauzula je NIL ako je prazna, sve se pokratilo
        print(" v ".join(list(clause1)) + "  +  " + " v ".join(list(clause2)) + "  ->  NIL")
    else:
        print(" v ".join(list(clause1)) + "  +  " + " v ".join(list(clause2)) + "  ->  " + " v ".join(list(clause)))
    printed_clauses.add(clause)

# Rezolucijski algoritam napisan je po primjeru na pseudokod funkcije plResolution danog na 6. prezentaciji sa predavanja. Unutar beskonačne petlje
# vrti duplu for petlju unutar kojih pokušava dokazati zadanu klauzulu. Algoritam je obogaćen korištenjem SoS skupa te
# micanjem redundantnih i tautoloških klauzula čime je ubrzan, tj optimiran. Osim toga, algoritam uz pomoć funkcije
# print_solution rekurzivno ispisuje bitne klauzule koje su bile korištene za stvaranje NILa.
def resolution(clauses, goal_clause):
    #negiraj svaki literal klauzule koja se dokazuje
    negated_goal = {tuple({literal[1:] if literal.startswith("~") else "~" + literal}) for literal in goal_clause}
    print("Given clauses:") #ispisi sve zadane klauzule
    for clause in clauses:
        print(" v ".join(list(clause)))
    print("Clauses from negating goal clause: ")
    for clause in negated_goal: #ispisi sve literale dobivene negiranjem ciljne klauzule
        print(" v ".join(list(clause)))
    print("======================================")
    clauses.update(negated_goal) #dodaj negirane literale u skup klauzula i u SoS skup
    SoS = set(negated_goal)
    parent_clauses = {} #rjecnik u kojem cu drzati roditelje klauzula
    
    while True:
        new_clauses = set() #novodobivene klauzule
        for clause1 in list(SoS): # STRATEGIJA SKUPA POTPORE -> barem jedna klauzula ce doci iz SoS skupa
            for clause2 in list(clauses.union(SoS)): #druga klauzula moze biti iz bilo kojeg skupa
                if clause1 == clause2:
                    continue
                useful_resolvent = True # zastavica koja gleda je li mi rezolventa korisna
                resolvent = set(clause1).union(clause2) #resolventa mi je za sada unija te dvije klauzule
                found_complementary_pair = False #par komplementarnih literala koji ce se pokratiti

                for literal in clause1:
                    negated_literal = literal[1:] if literal.startswith("~") else "~" + literal
                    if negated_literal in clause2: #ako nademo negirani literal 
                        found_complementary_pair = True #postavi zastavicu
                        break #dalje nas ne zanima jer kratimo samo 1 par komplementarnih literala
                if found_complementary_pair:
                    resolvent.discard(literal) # izbaci par komplementarnih literala iz rezolvente
                    resolvent.discard(negated_literal)
                if len(resolvent) == 0: #ako je duljina rezolvente 0, tj pokratilo se sve moguce, dosli smo do NILa
                    parent_clauses[tuple(resolvent)] = (tuple(clause1), tuple(clause2))
                    printed_clauses = set() #set koji ce u rekurziji pratiti sve vec ispisane klauzule
                    visited_clauses = set() #set koji ce u rekurziji pratiti sve vec posjecene klauzule
                    print_solution(tuple(resolvent), parent_clauses, printed_clauses, visited_clauses) #pozovi print fju za resolventu                    
                    print("======================================")
                    print("[CONCLUSION]: " + (" v ").join(list(goal_clause)) + " is true")
                    return True
                for literal in resolvent:
                    negated_literal = literal[1:] if literal.startswith("~") else "~" + literal
                    if negated_literal in resolvent: #ako u rezolventi imam tautologiju onda mi je beskorisna i ne dodajem je nigdje
                        useful_resolvent = False
                        break
                if resolvent in SoS:
                    useful_resolvent = False #ako je vec u SoSu takoder mi je beskorisna
                for clause in list(clauses.union(SoS)): #za sve postojece klauzule
                    if set(clause).issubset(resolvent): #ako je rezolventa redundantna
                        useful_resolvent = False #onda mi je beskorisna
                    elif resolvent.issubset(clause): #inace ako je ta kluazula sa kojom se usporeduje redundantna
                        if clause in clauses:
                            clauses.remove(clause) #makni je iz kojeg kod skupa dolazi
                        if clause in SoS:
                            SoS.remove(clause) #makni je iz kojeg kod skupa dolazi
                if useful_resolvent: #ako je rezolventa dobra
                    new_clauses.add(tuple(resolvent)) #dodaj je u skup novokreiranih klauzula
                    parent_clauses[tuple(resolvent)] = (tuple(clause1), tuple(clause2)) #zapisi njezine roditelje od kojih je nastala

        if not new_clauses: #ako se nije generirala niti jedna nova klauzula znaci da je algoritam gotov i nije dokazao zeljenu klauzulu
            print("[CONCLUSION]: " + (" v ").join(list(goal_clause)) + " is unknown")
            return False
        SoS.update(new_clauses) #na kraju dodaj sve novokreirane klauzule u SoS i skup svih klauzula
        clauses.update(new_clauses)


algorithm = sys.argv[1]
if algorithm == "resolution":
    input_file = sys.argv[2]
    clauses = set()
    goal_clause = None

    with open(input_file, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if not line.startswith("#"): #ignoriraj komentar linije
                literals = line.strip().lower().split(" v ") #podijeli sve literale jedne klauzule
                clause = tuple(set(literals)) #klauzula je tuple literala, set mice duplice
                if i != len(lines) - 1:  
                    clauses.add(clause)
                else:
                    goal_clause = clause #klauzula koja se dokazuje je zadnja na redu

    non_tautological_clauses = set() #set za izbacivanje tautologije
    for clause in clauses:              
        has_tautology = False
        for literal in clause: 
            if literal.startswith('~'):
                negated_literal = literal[1:] #negiraj literal
                if negated_literal in clause: #ako je u negirani u klauzuli znaci da je tautologija
                    has_tautology = True
            else:
                negated_literal = '~' + literal #negiraj literal
                if negated_literal in clause:
                    has_tautology = True #ako je u negirani u klauzuli znaci da je tautologija
        if not has_tautology:
            non_tautological_clauses.add(clause) #ako je sve u redu dodaj klauzulu

    redundant_clauses = set()
    for clause1 in non_tautological_clauses:
        for clause2 in non_tautological_clauses:
            if clause1 != clause2 and set(clause1).issubset(set(clause2)): #ako je klauzula podskup neke druge
                redundant_clauses.add(clause2) #onda nam je ta druga(duza) beskorisna

    clauses = non_tautological_clauses.difference(redundant_clauses) #zadrzi samo netutoloske i neredundantne klauzule 
    
    resolution(clauses, goal_clause) #pozovi rezolucijsku funckiju sa skupom klauzula i klauzulom koju pokusavamo dokazati

if algorithm == "cooking":
    input_file = sys.argv[2] #baza znanja
    user_commands = sys.argv[3] #file sa naredbama koje korisnik zeli provesti
    clauses = set()
    #sve isto kao i u algoritmu resolution, klauzule se skupe, nakon toga se izbaci tautologija, a nakon toga redundancija, 
    #jedina razlika je sto ovdje zadnji redak nije klauzula koja se treba dokazati
    with open(input_file, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if not line.startswith("#"):
                literals = line.strip().lower().split(" v ")
                clause = tuple(set(literals))
                clauses.add(clause)

    non_tautological_clauses = set()
    for clause in clauses:              
        has_tautology = False
        for literal in clause: 
            if literal.startswith('~'):
                negated_literal = literal[1:]
                if negated_literal in clause:
                    has_tautology = True
            else:
                negated_literal = '~' + literal
                if negated_literal in clause:
                    has_tautology = True
        if not has_tautology:
            non_tautological_clauses.add(clause)

    redundant_clauses = set()
    for clause1 in non_tautological_clauses:
        for clause2 in non_tautological_clauses:
            if clause1 != clause2 and set(clause1).issubset(set(clause2)):
                redundant_clauses.add(clause2)

    clauses = non_tautological_clauses.difference(redundant_clauses)

    with open(user_commands, 'r') as file:
        lines = file.readlines()
        for line in lines:
            command = line[-2] #simbol + - ili ?
            input_clause = line[:-3] #klauzula zadana prije simbola
            literals = input_clause.strip().lower().split(" v ")
            clause = tuple(set(literals))
            
            if command == "-":
                if clause in clauses:
                    clauses.discard(clause) #makni zadanu klauzulu iz skupa klauzula
            
            elif command == "+":
                clauses.add(clause) #dodaj zadanu klauzulu u skup klauzula
            
            elif command == "?":
                print()
                print("User’s command: " + line)
                print()
                #ponovno provjeri tautologiju  i redundanciju u slucaju da je dodana neka nova klauzula
                non_tautological_clauses = set()
                for clause2 in clauses:              
                    has_tautology = False
                    for literal in clause2: #check tautology
                        if literal.startswith('~'):
                            negated_literal = literal[1:]
                            if negated_literal in clause2:
                                has_tautology = True
                        else:
                            negated_literal = '~' + literal
                            if negated_literal in clause2:
                                has_tautology = True
                    if not has_tautology:
                        non_tautological_clauses.add(clause2)

                redundant_clauses = set()
                for clause1 in non_tautological_clauses:
                    for clause2 in non_tautological_clauses:
                        if clause1 != clause2 and set(clause1).issubset(set(clause2)):
                            redundant_clauses.add(clause2)

                clauses = non_tautological_clauses.difference(redundant_clauses)
                resolution(clauses.copy(), clause) #pozovi rezolucijski algoritam sa skupom svih klauzula, dokazuje se zadana klauzula