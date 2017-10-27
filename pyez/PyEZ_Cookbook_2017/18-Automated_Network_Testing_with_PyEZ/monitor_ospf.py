from jnpr.junos import Device                              # (1)
from jnpr.junos.op.ospf import OspfNeighborTable
import smtplib

MAIL_LOGIN = "user@example.com"                            # (2)
MAIL_PW = "xxx"
TO_ADDR = "admin@example.com"
MAIL_SERVER = "smtp.example.com"
SMTP_SSL_PORT = 587
SUBJ = "OSPF adjacency test results"

USER = "lab"                                               # (3)
PASSWD = "lab123"
R1 = "10.254.0.35"
R2 = "10.254.0.37"
R3 = "10.254.0.38"

def check_ospf_full_adjacencies(dev, neighbor_count):      # (4)
    ospf_table = OspfNeighborTable(dev)    # Create an instance of the Table
    ospf_table.get()                       # Populate the Table
    if len(ospf_table) != neighbor_count:
        return False
    for neighbor in ospf_table:
        if neighbor["ospf_neighbor_state"] != "Full":
            return False
    return True

def str_result(test_result):                               # (5)
    return "Success" if test_result else "Fail"

def main():                                                # (6)
    with Device(host=R1, user=USER, password=PASSWD) as dev:
        result1 = check_ospf_full_adjacencies(dev, 3)
        print("Test OSPF adjacencies on R1: " + str_result(result1))

    with Device(host=R2, user=USER, password=PASSWD) as dev:
        result2 = check_ospf_full_adjacencies(dev, 3)
        print("Test OSPF adjacencies on R2: " + str_result(result2))

    with Device(host=R3, user=USER, password=PASSWD) as dev:
        result3 = check_ospf_full_adjacencies(dev, 2)
        print("Test OSPF adjacencies on R3: " + str_result(result3))

    print("Sending email.")                                # (7)

    body_msg = "Test results: %s, %s, %s\n" % (str_result(result1),
                                               str_result(result2),
                                               str_result(result3))
    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s\n" % (MAIL_LOGIN,
                                                     TO_ADDR, SUBJ, body_msg)
    mailserver = smtplib.SMTP(MAIL_SERVER, SMTP_SSL_PORT)
    mailserver.starttls()
    mailserver.login(MAIL_LOGIN, MAIL_PW)
    mailserver.sendmail(MAIL_LOGIN, TO_ADDR, msg)
    mailserver.quit()

if __name__ == "__main__":                                 # (8)
    main()
