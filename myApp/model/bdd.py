from . import bddGen
import inspect
import hashlib
from datetime import datetime


def func_name():
    return inspect.currentframe().f_back.f_code.co_name

def get_membresData():
    sql="SELECT idutilisateur, pseudo, mail, nom, prenom, statut FROM utilisateur;"
    return bddGen.selectData(func_name(),sql,None)
def check_pseudo(pseudo):
    sql="SELECT * FROM utilisateur where pseudo=%s;"
    param=(pseudo,)
    return bddGen.selectOneData(func_name(),sql,param)

def check_email(email):
    sql="SELECT * FROM utilisateur where mail=%s;"
    param=(email,)
    return bddGen.selectOneData(func_name(),sql,param)

def verifLogin(login):
    sql="SELECT * FROM utilisateur WHERE pseudo=%s OR mail=%s;"
    param=(login, login)
    return bddGen.selectOneData(func_name(), sql, param)

def getMdp(idutilisateur):
    sql="SELECT mdp FROM utilisateur WHERE idutilisateur=%s;"
    param=(idutilisateur,)
    return bddGen.selectOneData(func_name(),sql,param)['mdp']

def add_userData(rform,mdp_hash,msg):
    sql="INSERT INTO utilisateur (pseudo, mail,mdp,nom,prenom,statut) VALUES (%s,%s,%s, %s, %s, %s);"
    param= (rform['pseudo'],rform['email'], mdp_hash, rform['lastname'],
            rform['firstname'], rform['statut'])
    return bddGen.addData(func_name(),sql,param,msg)   ##ce qu'on veut rentrer dans la base mais on veut mdp haché

def update_userMdpData(newMdp,iduser):
    sql="UPDATE utilisateur SET mdp=%s where idutilisateur=%s;"
    param=(newMdp,iduser)
    return bddGen.updateData(func_name(),sql,param, None)

def verifAuthData(login, mdp):
    sql = 'SELECT * FROM utilisateur WHERE pseudo=%s OR mail=%s;'
    param = (login, login)
    user = bddGen.selectOneData(func_name(), sql, param, None)
    if not user:
        return None

    mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
    mdp_stocke = user.get('mdp')

    if mdp_stocke == mdp_hash or mdp_stocke == mdp:
        return user

    return None

def get_userById(idutilisateur):
    sql = "SELECT idutilisateur, pseudo, mail, nom, prenom, statut FROM utilisateur WHERE idutilisateur=%s;"
    param = (idutilisateur,)
    return bddGen.selectOneData(func_name(), sql, param, None)

def delete_userData(idutilisateur, msg):
    sql = "DELETE FROM utilisateur WHERE idutilisateur=%s;"
    param = (idutilisateur,)
    return bddGen.deleteData(func_name(), sql, param, msg)

def create_paquet(nompaquet, idcreateur, public):
    sql = " INSERT INTO paquet(datecreation, idcreateur, nompaquet, public) VALUES(NOW(), %s, %s, %s);"
    param = (idcreateur, nompaquet, public)
    return bddGen.addData(func_name(), sql, param, None)


def get_paquets_user(idcreateur):
    if idcreateur is None:
        return []
    sql = """ SELECT idpaquet, nompaquet, datecreation, public FROM paquet
    WHERE idcreateur=%s ORDER BY datecreation DESC;"""
    param = (idcreateur,)
    return bddGen.selectData(func_name(), sql, param)

def delete_paquet(idpaquet, idcreateur):
    sql = " DELETE FROM paquet WHERE idpaquet = %s AND idcreateur = %s;"
    param = (idpaquet, idcreateur)
    return bddGen.deleteData(func_name(), sql, param)


def update_paquet(idpaquet, nompaquet, public):
    sql = " UPDATE paquet SET nompaquet = %s, public = %s WHERE idpaquet = %s;"
    param = (nompaquet, public, idpaquet)
    return bddGen.updateData(func_name(), sql, param)

def get_one_paquet(idpaquet, idcreateur):
    sql = " SELECT * FROM paquet WHERE idpaquet = %s AND idcreateur = %s; "
    param = (idpaquet, idcreateur)
    return bddGen.selectOneData(func_name(), sql, param)

def get_liste_public():
    sql = """
        SELECT p.idpaquet,
               p.nompaquet,
               p.datecreation,
               p.public,
               c.nomcategorie AS nomcategorie
        FROM paquet p
        LEFT JOIN categorie c ON p.idcategorie = c.idcategorie
        WHERE p.public = 1
        ORDER BY p.datecreation DESC
    """
    return bddGen.selectData(func_name(), sql, None)

def get_nombrecartes_user(idutilisateur):
        sql = """
                SELECT COUNT(*) AS nb
                FROM revision r
                LEFT JOIN boite b ON r.idboite = b.idboite
                WHERE r.idutilisateur = %s
                    AND (
                        r.date_derniere_revision IS NULL
                        OR DATE_ADD(r.date_derniere_revision, INTERVAL COALESCE(b.duree, 0) DAY) <= CURDATE()
                    )
        """
        param = (idutilisateur,)
        return bddGen.selectOneData(func_name(), sql, param)

def get_liste_iduser(idutilisateur):
    sql = """
        SELECT p.idpaquet,
               p.datecreation,
               p.idcreateur,
               p.idcategorie,
               p.nompaquet,
               p.public,
               COUNT(c.idcarte) AS nb_cartes
        FROM paquet p
        LEFT JOIN carte c ON c.idpaquet = p.idpaquet
        WHERE p.idcreateur = %s
        GROUP BY p.idpaquet, p.datecreation, p.idcreateur, p.idcategorie, p.nompaquet, p.public
        ORDER BY p.datecreation DESC
    """
    param =(idutilisateur,)
    return bddGen.selectData(func_name(),sql,param)

def get_cartes_by_paquet(idpaquet):
    sql = "SELECT * FROM carte WHERE idpaquet=%s;"
    param = (idpaquet,)
    return bddGen.selectData(func_name(), sql, param, None)

def add_carte(question, reponse, idpaquet, msg):
    sql = "INSERT INTO carte (question, reponse, idpaquet) VALUES (%s, %s, %s);"
    param = (question, reponse, idpaquet)
    return bddGen.addData(func_name(), sql, param, msg)

def update_carte(idcarte, question, reponse, msg):
    sql = "UPDATE carte SET question=%s, reponse=%s WHERE idcarte=%s;"
    param = (question, reponse, idcarte)
    return bddGen.updateData(func_name(), sql, param, msg)

def delete_carte(idcarte, msg):
    sql = "DELETE FROM carte WHERE idcarte=%s;"
    param = (idcarte,)
    return bddGen.deleteData(func_name(), sql, param, msg)

def get_carte_by_id(idcarte):
    sql = "SELECT * FROM carte WHERE idcarte=%s;"
    param = (idcarte,)
    return bddGen.selectOneData(func_name(), sql, param, None)

def get_paquets_revision(idutilisateur):
    sql = """ SELECT p.idpaquet, p.nompaquet, 
              COALESCE(c.nomcategorie, 'Sans catégorie') as nomcategorie
              FROM paquet p LEFT JOIN categorie c
              ON p.idcategorie = c.idcategorie
              WHERE p.idcreateur=%s
              ORDER BY c.nomcategorie, p.nompaquet"""
    param = (idutilisateur,)
    return bddGen.selectData(func_name(), sql, param) 

def get_revision(idutilisateur, idcarte):
    sql = "SELECT * FROM revision WHERE idutilisateur=%s AND idcarte=%s;"
    param = (idutilisateur, idcarte)
    return bddGen.selectOneData(func_name(), sql, param, None)

def add_revision(idutilisateur, idcarte, idboite):
    sql = "INSERT INTO revision (idutilisateur, idcarte, idboite, date_derniere_revision) VALUES (%s, %s, %s, NOW());"
    param = (idutilisateur, idcarte, idboite)
    return bddGen.addData(func_name(), sql, param, None)

def update_revision(idutilisateur, idcarte, idboite):
    sql = "UPDATE revision SET idboite=%s, date_derniere_revision=NOW() WHERE idutilisateur=%s AND idcarte=%s;"
    param = (idboite, idutilisateur, idcarte)
    return bddGen.updateData(func_name(), sql, param, None)

def get_cartes_a_reviser(idutilisateur, idpaquet):
    sql = """
        SELECT c.idcarte, c.question, c.reponse,
               COALESCE(r.idboite, 1) as idboite
        FROM carte c
        LEFT JOIN revision r ON r.idcarte = c.idcarte 
            AND r.idutilisateur = %s
        LEFT JOIN boite b ON b.idboite = r.idboite
        WHERE c.idpaquet = %s
        AND (
            r.idcarte IS NULL
            OR DATE_ADD(r.date_derniere_revision, INTERVAL COALESCE(b.duree, 1) DAY) <= NOW()
        );
    """
    param = (idutilisateur, idpaquet)
    return bddGen.selectData(func_name(), sql, param, None)