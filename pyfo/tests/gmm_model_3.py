#
# A silly model with over 100'000 nodes to stress test the compiler
#

def sample_component(pi):
    return sample(categorical(pi))

def observe_data(n):
    obs = ys[n]
    if zs[n] == 0:
        observe(normal(mus[0], 1), obs)
    else:
        observe(normal(mus[1], 1), obs)

ys = [-2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3,  3.2,  0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8,
      -1.7, -1.3, 3.2, 0.8, -0.9, 0.3, 1.4, 2.1, 0.8, 1.9,
      -2.0, -2.5, -1.7, -1.9, -2.2, 1.5, 2.2, 3.0, 1.2, 2.8] * 100

pi = sample(dirichlet([1.0, 1.0]))
zs = [sample_component(pi) for _ in range(len(ys))]
mus = [sample(normal(0, 100)), sample(normal(0, 100))]
for i in range(len(ys)):
    observe_data(i)
[pi, zs, mus]