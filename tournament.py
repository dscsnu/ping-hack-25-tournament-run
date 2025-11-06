import os
from tabulate import tabulate

stratergies = [] #contains the name of each file
scores = {} #contains key as the file_name and value a dict of keys "wins","losses","points"
N = 0
results = {}

def tournamentSetup():
    cwd = os.getcwd()
    submissions_dir = cwd+"\submissions"
    submission_files = os.listdir(submissions_dir) #lists all files inside the submission dir
    for submission in submission_files:
        stratergies.append(submission[:-3])    
        scores[submission[:-3]] = {"wins":0,"losses":0,"points":0}
    N = len(stratergies)
    stratergies.sort()

def sortResults():
    results = dict(sorted(scores.items(), key=lambda item: item[1]['points'], reverse=True))

# def match(player1, player2): #dummy function for testing
#     return (player1,300,300,399)
# res_i = [("ab123",600,200,199),("cd456",500,300,199),("bc256",400,400,199)] # for testing
def tournamentRunMatches():
    for i in range(N):
        for j in range(i+1,N):
            p1 = stratergies[i]
            p2 = stratergies[j]
            if p1 == p2:
                continue
            #res = res_i[k]
            res = match(p1,p2) #match function call
            updateScores(res,p1,p2)
    sortResults()
    SaveResults("ping_hack_25_results.txt")

def updateScores(res,p1,p2):
    if res[0] == p1:
        scores[p1]["wins"] += 1
        scores[p1]["points"] += res[1]*3
        scores[p1]["points"] += res[3]*1
        scores[p2]["losses"] += 1
        scores[p2]["points"] += res[3]*1

    else:
        scores[p2]["wins"] += 1
        scores[p2]["points"] += res[1]*3
        scores[p2]["points"] += res[3]*1
        scores[p1]["losses"] += 1
        scores[p1]["points"] += res[3]*1

def playoffsRun():
    first = results.items()[0][0]
    second = results.items()[1][0]
    third = results.items()[2][0]
    fourth = results.items()[3][0]
    q1 = match(first,second)
    updateScores(q1,first,second)
    if(q1[0] == first):
        SavePlayoffResults("Qualifier 1","ping_hack_25_results.txt",first,second)
    else:
        SavePlayoffResults("Qualifier 1","ping_hack_25_results.txt",second,first)
    eliminator = match(third,fourth)
    updateScores(eliminator,third,fourth)
    if(eliminator[0] == third):
        SavePlayoffResults("Eliminator","ping_hack_25_results.txt",third,fourth)
    else:
        SavePlayoffResults("Eliminator","ping_hack_25_results.txt",third,fourth)
    if q1[0]==first:
        q2 = match(second,eliminator[0])
        updateScores(q2,second,eliminator[0])
        if q2[0] == second:
            SavePlayoffResults("Qualifier 2","ping_hack_25_results.txt",second,eliminator[0])
            final = match(first,second)
            updateScores(final,first,second)
            if final[0] == first:
                SavePlayoffResults("Final","ping_hack_25_results.txt",first,second)
            else:
                SavePlayoffResults("Final","ping_hack_25_results.txt",second,first)
        else:
            SavePlayoffResults("Qualifier 2","ping_hack_25_results.txt",eliminator[0],second)
            final = match(first,eliminator[0])
            updateScores()
            if final[0] == first:
                SavePlayoffResults("Final","ping_hack_25_results.txt",first,eliminator[0])
            else:
                SavePlayoffResults("Final","ping_hack_25_results.txt",eliminator[0],first)
    else:
        q2 = match(first,eliminator[0])
        updateScores(q2,first,eliminator[0])
        if q2[0] == first:
            SavePlayoffResults("Qualifier 2","ping_hack_25_results.txt",first,eliminator[0])
            final = match(second,first)
            updateScores(final,second,first)
            if final[0] == second:
                SavePlayoffResults("Final","ping_hack_25_results.txt",second,first)
            else:
                SavePlayoffResults("Final","ping_hack_25_results.txt",first,second)
            
        else:
            SavePlayoffResults("Qualifier 2","ping_hack_25_results.txt",eliminator[0],first)
            final = match(second,eliminator[0])
            updateScores(final,second,eliminator[0])
            if final[0] == second:
                SavePlayoffResults("Final","ping_hack_25_results.txt",second,eliminator[0])
            else:
                SavePlayoffResults("Final","ping_hack_25_results.txt",eliminator[0],second)
    

def SaveResults(filename):
    tabulateable_results = []
    k = 0
    for item in results.items():
        tabulateable_results.append([])
        tabulateable_results[k].append(item[0])
        tabulateable_results[k].append(item[1]['wins'])
        tabulateable_results[k].append(item[1]['losses'])
        tabulateable_results[k].append(item[1]['points'])
        k = k+1

    headers = ["Contestant","Wins","Losses","Points"]
    to_save = tabulate(tabulateable_results,headers=headers,tablefmt="grid")
    with open(filename,"w") as f:
        f.write(to_save)
        f.write("\n")
        f.write("-"*30)

def SavePlayoffResults(match_name,filename,winner,loser):
    tabulateable_results = []
    with open(filename,"a") as f:
        f.write(match_name)
        f.write("\n")
        f.write("Winner :",winner)
        f.write("\n")
        tabulateable_results.append([])
        tabulateable_results[0].append(winner)
        tabulateable_results[0].append(results[winner]['wins'])
        tabulateable_results[0].append(results[winner]['losses'])
        tabulateable_results[0].append(results[winner]['points'])
        f.write("\n")
        f.write("Loser :",loser)
        f.write("\n")
        tabulateable_results.append([])
        tabulateable_results[0].append(loser)
        tabulateable_results[0].append(results[loser]['wins'])
        tabulateable_results[0].append(results[loser]['losses'])
        tabulateable_results[0].append(results[loser]['points'])
        f.write("-"*30)

tournamentSetup()
tournamentRunMatches()
tournamentRunMatches()
playoffsRun()