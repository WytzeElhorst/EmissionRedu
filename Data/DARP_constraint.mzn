%Model 2: Based on the model described in section 3.2 of https://www.tandfonline.com/doi/full/10.1080/0305215X.2021.1996570?scroll=top&needAccess=true&role=tab

%Parameters
int: n;                                            % number of requests
int: K;                                            % number of vehicles
set of int: V = 1..K;                              % set of vehicles
set of int: J = 1..n;                              % set of orders               
set of int: P = 1..n;                              % pick up requests
set of int: D = n+1..2*n;                          % drop off requests
set of int: N = 1..2*n+2;                          % set of all requests + depot
array[V] of int: capacity;                         % vehicle capacity
array[N] of int: load;                             % load (number of passengers) for each request
array[N] of int: e_start;                          % earliest pickup time for each request
array[N] of int: l_start;                          % latest dropoff time for each request
array[N, N] of int: t_cost;                        % travel cost matrix between all request points
array[N, N] of int: t_time;                        % travel time matrix between all request points
array[V, N, N] of int: M;

% decision variables
array[V, N, N] of var bool: routes;                % routes[i,j,k] = 1 if vehicle k travels from i to j, else 0
array[V, N] of var int: B;                         % time at which vehicle k starts servicing request i
array[V, N] of var int: Q;                         % current load of vehicle k after request i

% constraints
constraint forall(i in P)(
  sum(k in vehicles, j in REQ)(routes[i,j,k]) = 1);  