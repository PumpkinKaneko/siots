These programs function as demo program of PBFT which is a consensus algorithm.
This should be run on 3 or more PCs with python3.

How to run
  Download these files to your PCs.
  Pip3 install pycrypto, websocket-server and websocket-client to your PCs.
  Decide which PCs will be core-node.
  Rewrite core_address.txt of core-node PCs based on example.
  Rewrite each leaf_address.txt too.
  Run PBFT_core.py on core-node PCs, and input "ok" if all of core-node PCs run it.
  Run PBFT_leaf.py on any one of your PCs.
  If you input data on PBFT_leaf.py correctly, ledger.txt of core-node PCs will be rewritten

Process of PBFT
1 A leaf-node send transaction with signature to a core-node.
    (In these programs use simple RSA crypto.)
2 Core-node received transaction send that to other core-nodes.
3 Core-nodes check transaction.
4 If it was not rewritten, core-nodes send ok-signal to other core-nodes.
5 When core-nodes receive ok-signal from core-nodes more than supermajority of all, write transaction to ledger.
    (In these programs supermajority is 2/3.)
6 After writing, core-nodes tell leaf-node that transaction is over.
7 One transaction finish.
