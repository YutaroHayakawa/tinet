
docker exec H1 birdc6 -v show ospf nei ospf_func1_up | grep -v "0001 BIRD 1.6.6 ready"
docker exec H1 birdc6 -v show ospf nei ospf_func1_dn | grep -v "0001 BIRD 1.6.6 ready"
docker exec H1 birdc6 -v show ospf nei ospf_func2_up | grep -v "0001 BIRD 1.6.6 ready"
docker exec H1 birdc6 -v show ospf nei ospf_func2_dn | grep -v "0001 BIRD 1.6.6 ready"
