%Model 1: Based on the model described in section 3.1 of https://link.springer.com/article/10.1007/s10479-007-0170-8

%Parameters
int: n;                                        % number of requests
int: K;                                        % number of vehicles
int: L;                                        % max ride time
set of int: vehicles = 0..K-1;                 % set of all vehicles
set of int: REQ = 0..2*n+1;                    % set of all requests
set of int: P = 1..n;                          % pick up requests
set of int: D = n+1..2*n;                      % drop off requests
array[vehicles] of int: capacity;              % vehicle capacity
array[vehicles] of int: max_r_time;            % maximum allowed time for each route
array[REQ] of int: load;                       % load (number of passengers) for each request
array[REQ] of int: service_time;               % time required for pickup/dropoff at each request
array[REQ] of int: earliest_pickup;            % earliest pickup time for each request
array[REQ] of int: latest_dropoff;             % latest dropoff time for each request
array[REQ, REQ, vehicles] of int: t_cost;      % travel cost matrix between all request points
array[REQ, REQ, vehicles] of int: t_emission;  % travel cost matrix between all request points
array[REQ, REQ] of int: t_time;                % travel time matrix between all request points

% decision variables
array[REQ, REQ, vehicles] of var bool: routes; % routes[i,j,k] = 1 if vehicle k travels from i to j, else 0
array[REQ, vehicles] of var int: s_time;       % time at which vehicle k starts servicing request i
array[REQ, vehicles] of var int: c_load;       % current load of vehicle k after request i
array[P, vehicles] of var int: ride_time;      % ride time of user i in vehicle k
array[P, vehicles] of var int: wait_time;      % time between pickup and earliest available time

% constraints
constraint forall(i in P)(
  sum(k in vehicles, j in REQ)(routes[i,j,k]) = 1);                                                % 2: each request must be served once

constraint forall(k in vehicles)(
  sum(i in REQ)(routes[0,i,k]) = 1 /\ sum(i in REQ)(routes[i,2*n+1,k]) = 1);                       % 3: each vehicle starts and ends at the depot

constraint forall(i in P, k in vehicles)(
  sum(j in REQ)(routes[i,j,k]) - sum(j in REQ)(routes[i+n,j,k]) = 0);                              % 4: ensures pickup & drop off is done by the same vehicle

constraint forall(i in P union D, k in vehicles)(
  sum(j in REQ)(routes[j,i,k]) - sum(j in REQ)(routes[i,j,k]) = 0);                                % 5: each non-depot location is traveled to and from once per vehicle

constraint forall(i,j in REQ, k in vehicles)(
  s_time[j,k] >= (s_time[i,k] + service_time[i] + t_time[i,j])*routes[i,j,k]);                     % 6: Start time of req is >= to start time of prev req + service & travel time

constraint forall(i,j in REQ, k in vehicles)(
  c_load[j,k] >= (c_load[i,k] + load[j])*routes[i,j,k]);                    % 7: Vehicle load at j is >= to load at previous request plus load of new request
  
constraint forall(i in P, k in vehicles)(
  ride_time[i,k] >= s_time[n+i,k] - (s_time[i,k] + service_time[i]));        % 8: customer ride time is drop off time minus pick up & service time

constraint forall(k in vehicles)(
  s_time[2*n+1,k] - s_time[0, k] <= max_r_time[k]);                                              % 9: total route duration can not exceed max time
  
constraint forall(i in REQ, k in vehicles)(
  earliest_pickup[i] <= s_time[i,k] /\ s_time[i,k] <= latest_dropoff[i]);     % 10: start time for each request is between earliest pickup and latest drop off
  
constraint forall(i in P, k in vehicles)(
  t_time[i, n+i] <= ride_time[i,k] /\ ride_time[i,k] <= L);                % 11: time to get from pick up to drop off is <= user ride time <= max ride time 
  
constraint forall(i,j in P, k in vehicles)(                              % 12: wait time between earliest pick up and actual pick up time
  wait_time[i, k] >= s_time[i, k] - earliest_pickup[i]);

constraint forall(k in vehicles)(
  sum(i in REQ)(routes[i, i, k]) = 0);
 
constraint forall(k in vehicles)(
  sum(i in D)(routes[0, i, k]) = 0);
  
constraint forall(k in vehicles)(
  routes[0, 2*n+1, k] = 0);
  
constraint forall(i in REQ, k in vehicles)(
  max(0, load[i]) <= c_load[i,k] /\ c_load[i,k] <= min(capacity[k], capacity[k] + load[i]));  % 12: current load is at least as large as load of current        request, load <= max capacity


% solve the problem
solve minimize(sum(k in vehicles, i in P, j in REQ)(ride_time[i, k] * routes[i,j,k]));   % objective is to minimize start time of each request

% output the solution
output ["Avarage customer waiting time: " ++ show(sum(k in vehicles, i in P, j in REQ)(wait_time[i, k] * routes[i,j,k]) / n) ++ " minutes \n Avarage customer ride duration: " ++ show(sum(k in vehicles, i in P,j in REQ)(ride_time[i, k] * routes[i,j,k]) / n) ++ " minutes"];
%output [show(routes[i, j, k]) ++ " " ++ if j == (2*n + 1) then "\n" else "" endif | i,j in REQ, k in vehicles ] ++ ["total operational cost: " ++ show(sum(k in vehicles, i in REQ, j in REQ)(t_cost[i,j,k]*routes[i,j,k]))];