import thriftpy2

from thriftpy2.protocol import TCyBinaryProtocolFactory
from thriftpy2.transport import TCyBufferedTransportFactory
from thriftpy2.rpc import client_context
import re
calc_thrift = thriftpy2.load("masterworker.thrift", module_name="calc_thrift")

def main():
    """
        main function is the one which handles client side of things, few validation, command parsing etc

        :param :  No param required

        :return: void ,never ending function unless quit "command" is hit.
    """
    try:
        with client_context(calc_thrift.Calculator, '0.0.0.0', 6000,
                        proto_factory=TCyBinaryProtocolFactory(),
                        trans_factory=TCyBufferedTransportFactory(),socket_timeout=100000,connect_timeout=100000) as cal:
          while True:
            user_input = input("Enter command:")
            if user_input == "start server":
                ready_response = cal.state("ready")
                print(ready_response)

            elif user_input == "pause server":
                unready_response = cal.state("unready")
                print(unready_response)

            elif user_input == "terminate server":
                terminate_response = cal.state("terminate")
                print(terminate_response)

            elif user_input == "ping server":
                ping_response = cal.ping()
                print(ping_response)

            elif user_input == "quit":
                cal.close()
                break
            elif user_input[:9]=="calculate":
               try:
                 parameters=[i.strip() for i in re.split(r'''^\w+\(|\)$|((?:\([^()]*\)|'[^']*'|"[^"]*"|[^'"(),])*)''', user_input) if
                  i and i != ',']
                 calculate_response = cal.calculate(float(parameters[0]),parameters[1])
                 print(calculate_response)
               except Exception:
                   print("Incorrect syntax. Here is an example for calculate function -> calculate(1,'hello world') ")

            elif user_input == "":
                print("Command not found.")

            else:
                print("No matching command not found.")
    except Exception:
        print("Server is not running")


if __name__ == '__main__':
    main()