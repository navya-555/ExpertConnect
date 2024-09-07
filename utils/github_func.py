from numpy import array, ndim, newaxis
from itertools import product
from sklearn.metrics.pairwise import cosine_similarity



def similarity_score(arr1,arr2):
    skill_score = cosine_similarity([arr1[0]],[arr2[0]])[0][0]
    domain_score = cosine_similarity([arr1[0]],[arr2[0]])[0][0]

    calc_similarity = 0.4 * skill_score + 0.6 * domain_score

    return calc_similarity


def compute_score_pair(pair1,pair2):
    if(len(pair1)==2 and len(pair2)==2):
        return similarity_score(pair1,pair2)
    elif (len(pair1)==2):
        return max(cosine_similarity([pair1[0]],[pair2[0]]),cosine_similarity([pair1[1]],[pair2[0]]))[0][0]
    elif (len(pair2)==2):
        return max(cosine_similarity([pair1[0]],[pair2[0]]),cosine_similarity([pair1[0]],[pair2[1]]))[0][0]
    else:
        return cosine_similarity([pair1[0]],[pair2[0]])[0][0]



def to_3d_array(arr):
    if ndim(arr) == 3 :
        return arr
    elif ndim(arr) == 2:
        return arr[newaxis, :, :]
    else:
        return  arr[newaxis, newaxis, :]



def compute_score(prof1,prof2):
    (prof1,prof2) = to_3d_array(array(prof1)),to_3d_array(array(prof2))
    return float(max([compute_score_pair(pairs[0],pairs[1]) for pairs in list(product(prof1,prof2))]))

