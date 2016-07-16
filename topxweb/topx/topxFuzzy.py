import numpy as np
import skfuzzy as fuzz
#import matplotlib.pyplot as plt
class TopxFuzzy(object):
    def calculaFuzzy(rep, pat, cor):
        #multiplicador
        multiplier = 10
        #entradas

        rep = rep*multiplier
        pat = pat*multiplier
        cor = cor*multiplier

        #gera funções universo
        max_rauthor = 4*multiplier+1
        max_patterns = 5*multiplier+1
        max_correct = 100*multiplier+1
        max_importance = 100

        author_reputation = np.arange(0, max_rauthor, 1)
        patterns = np.arange(0, max_patterns, 1)
        correctness = np.arange(0, max_correct, 1)
        importance = np.arange(0, max_importance, 1)

        #Funções de pertinencia para reputação do autor
        r_low = fuzz.trimf(author_reputation, [0, 0, 3*multiplier])
        r_medium = fuzz.trapmf(author_reputation, [0, 0.5*multiplier, 2*multiplier, 4*multiplier])
        r_high = fuzz.trapmf(author_reputation, [1*multiplier, 3*multiplier, 4*multiplier, max_rauthor])

        #funções de pertinencia para padrões
        p_low = fuzz.trapmf(patterns, [0, 0, 0.5*multiplier, 2*multiplier])
        p_medium = fuzz.trapmf(patterns, [0.5*multiplier, 1.5*multiplier, 3*multiplier, 4.5*multiplier])
        p_high = fuzz.trapmf(patterns, [2.5*multiplier, 4*multiplier, 5*multiplier, max_patterns])

        #funções de pertinencia para corretude
        c_low = fuzz.trapmf(correctness, [0, 0, 45*multiplier, 70*multiplier])
        c_medium = fuzz.trapmf(correctness, [40*multiplier, 60*multiplier, 80*multiplier, 90*multiplier])
        c_high = fuzz.trapmf(correctness, [70*multiplier, 95*multiplier, 100*multiplier, max_correct])

        #funções de pertinencia para a importancia
        i_insufficient = fuzz.trapmf(importance, [0, 0, 10, 20])
        i_sufficient = fuzz.trimf(importance, [20, 30, 50])
        i_good = fuzz.trimf(importance, [50, 60, 70])
        i_excellent = fuzz.trapmf(importance, [70, 90, 100, 101])
        # Visualizando função de pertinencia para reputação do autor
     #   fig, ax = plt.subplots()

      #  ax.plot(author_reputation, r_low, 'r', author_reputation, r_medium, 'm',
      #   author_reputation, r_high, 'b')
      #  ax.set_ylabel('Fuzzy membership')
      #  ax.set_xlabel('Author Reputation')
      #  ax.set_ylim(-0.05, 1.05)
      #  ax.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
         # it will place the legend on the outer right-hand side of the last axes

        # Visualizando função de pertinencia para padrões
        #fig, ax = plt.subplots()

     #   ax.plot(patterns, p_low, 'r', patterns, p_medium, 'm',
     #    patterns, p_high, 'b')
     #   ax.set_ylabel('Fuzzy membership')
     #   ax.set_xlabel('Patterns')
     #   ax.set_ylim(-0.05, 1.05)

        # Visualizando função de pertinencia para corretude
       # fig, ax = plt.subplots()

    #    ax.plot(correctness, c_low, 'r', correctness, c_medium, 'm',
      #   correctness, c_high, 'b')
     #   ax.set_ylabel('Fuzzy membership')
     #   ax.set_xlabel('Correctness')
    #    ax.set_ylim(-0.05, 1.05)

        # Visualizando função de pertinencia para reputação do autor
    #    fig, ax = plt.subplots()

    #    ax.plot(importance, i_insufficient, 'r', importance, i_sufficient, 'm',
    #     importance, i_good, 'b', importance, i_excellent, 'g')
    #    ax.set_ylabel('Fuzzy membership')
    #    ax.set_xlabel('Importance')
     #   ax.set_ylim(-0.05, 1.05)

        def reputhation_category(rep_in = 0):
            a_r_low = fuzz.interp_membership(author_reputation,r_low,rep_in)
            a_r_medium = fuzz.interp_membership(author_reputation,r_medium,rep_in)
            a_r_high = fuzz.interp_membership(author_reputation,r_high,rep_in)
            return dict(rep_low = a_r_low,rep_medium = a_r_medium, rep_high = a_r_high)

        def patterns_category(pat_in = 0):
            pat_low = fuzz.interp_membership(patterns, p_low, pat_in)
            pat_medium = fuzz.interp_membership(patterns, p_medium, pat_in)
            pat_high = fuzz.interp_membership(patterns, p_high, pat_in)
            return dict(patterns_low = pat_low,patterns_medium = pat_medium, patterns_high = pat_high)

        def correctness_category(cor_in = 0):
            cor_low = fuzz.interp_membership(correctness, c_low, cor_in)
            cor_medium = fuzz.interp_membership(correctness, c_medium, cor_in)
            cor_high = fuzz.interp_membership(correctness, c_high, cor_in)
            return dict(correct_low = cor_low,correct_medium = cor_medium, correct_high = cor_high)

        rep_in = reputhation_category(rep)
        pat_in = patterns_category(pat)
        cor_in = correctness_category(cor)
        #print("For reputhation  : ", rep_in)
        #print("For patterns     : ", pat_in)
        #print("For correctness  :", cor_in)

        rule1 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_low'], cor_in['correct_low']))
        rule2 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_low'], cor_in['correct_medium']))
        rule3 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_low'], cor_in['correct_high']))
        rule4 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_medium'], cor_in['correct_low']))
        rule5 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_medium'], cor_in['correct_medium']))
        rule6 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_medium'], cor_in['correct_high']))
        rule7 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_high'], cor_in['correct_low']))
        rule8 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_high'], cor_in['correct_medium']))
        rule9 = np.fmin(rep_in['rep_low'], np.fmin(pat_in['patterns_high'], cor_in['correct_high']))
        rule10 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_low'], cor_in['correct_low']))
        rule11 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_low'], cor_in['correct_medium']))
        rule12 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_low'], cor_in['correct_high']))
        rule13 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_medium'], cor_in['correct_low']))
        rule14 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_medium'], cor_in['correct_medium']))
        rule15 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_medium'], cor_in['correct_high']))
        rule16 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_high'], cor_in['correct_low']))
        rule17 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_high'], cor_in['correct_medium']))
        rule18 = np.fmin(rep_in['rep_medium'], np.fmin(pat_in['patterns_high'], cor_in['correct_high']))
        rule19 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_low'], cor_in['correct_low']))
        rule20 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_low'], cor_in['correct_medium']))
        rule21 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_low'], cor_in['correct_high']))
        rule22 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_medium'], cor_in['correct_low']))
        rule23 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_medium'], cor_in['correct_medium']))
        rule24 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_medium'], cor_in['correct_high']))
        rule25 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_high'], cor_in['correct_low']))
        rule26 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_high'], cor_in['correct_medium']))
        rule27 = np.fmin(rep_in['rep_high'], np.fmin(pat_in['patterns_high'], cor_in['correct_high']))

        imp1 = np.fmin(rule1, i_insufficient)
        imp2 = np.fmin(rule2, i_insufficient)
        imp3 = np.fmin(rule3, i_sufficient)
        imp4 = np.fmin(rule4, i_sufficient)
        imp5 = np.fmin(rule5, i_sufficient)
        imp6 = np.fmin(rule6, i_sufficient)
        imp7 = np.fmin(rule7, i_sufficient)
        imp8 = np.fmin(rule8, i_good)
        imp9 = np.fmin(rule9, i_excellent)
        imp10 = np.fmin(rule10, i_insufficient)
        imp11 = np.fmin(rule11, i_insufficient)
        imp12 = np.fmin(rule12, i_sufficient)
        imp13 = np.fmin(rule13, i_sufficient)
        imp14 = np.fmin(rule14, i_sufficient)
        imp15 = np.fmin(rule15, i_good)
        imp16 = np.fmin(rule16, i_good)
        imp17 = np.fmin(rule17, i_excellent)
        imp18 = np.fmin(rule18, i_excellent)
        imp19 = np.fmin(rule19, i_sufficient)
        imp20 = np.fmin(rule20, i_sufficient)
        imp21 = np.fmin(rule21, i_sufficient)
        imp22 = np.fmin(rule22, i_sufficient)
        imp23 = np.fmin(rule23, i_good)
        imp24 = np.fmin(rule24, i_good)
        imp25 = np.fmin(rule25, i_good)
        imp26 = np.fmin(rule26, i_excellent)
        imp27 = np.fmin(rule27, i_excellent)

        aggregate_membership = np.fmax(imp1, np.fmax(imp2, np.fmax(imp3, np.fmax(imp4, np.fmax(imp5, np.fmax(imp6,
         np.fmax(imp7, np.fmax(imp8, np.fmax(imp9, np.fmax(imp10, np.fmax(imp11, np.fmax(imp12, imp13)) )) ) )) ) )) ))
        aggregate_membership = np.fmax(aggregate_membership, np.fmax(imp14, np.fmax(imp15, np.fmax(imp16,
         np.fmax(imp17, np.fmax(imp18, np.fmax(imp19, np.fmax(imp20, np.fmax(imp21, np.fmax(imp22, np.fmax(imp23, np.fmax(imp24,
         np.fmax(imp25, np.fmax(imp26, imp27))))))))))))))
        result_importance = fuzz.defuzz(importance, aggregate_membership, 'centroid')

        result_importance = result_importance/10
        print('importance: ', result_importance)
   #     plt.legend()
        #plt.show()
        return result_importance




#top = TopxFuzzy()
#top.calculaFuzzy(4,1,80)