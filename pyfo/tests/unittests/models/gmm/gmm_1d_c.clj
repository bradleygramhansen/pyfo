;; fix pi, unknown prior mean for the center of each cluster

(defn sample-components [_ zs pi]
  (let [z (sample (categorical pi))]
    (conj zs z)))

(defn observe-data [n _ ys zs mus taus]
  (let [y (get ys n)
        z (get zs n)
        mu (get mus z)
        tau (get taus z)]
    (observe (normal mu (/ 1 tau)) y)
    nil))

(let [ys      (vector -2.0  -2.5  -1.7  -1.9  -2.2
                      1.5  2.2  3  1.2  2.8)
      k 2
      pi (sample (dirichlet [1.0 1.0]))
      zs  (loop 10 (vector) sample-components pi)
      mus (vector (sample (normal 0 100))   ; std = 10
                  (sample (normal 0 100)))
      taus (vector (sample (gamma 1 1))
                  (sample (gamma 1 1)))]
  (loop 10 nil observe-data ys zs mus taus)
  (vector pi zs mus taus ))