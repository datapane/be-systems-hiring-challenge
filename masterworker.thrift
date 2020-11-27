service Calculator {
  i64 ping();
  string calculate(1:double x, 2:string msg);
  string state(1:string command)
}