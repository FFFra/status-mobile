(ns status-im2.contexts.quo-preview.wallet.account-card
  (:require [react-native.core :as rn]
            [quo2.foundations.colors :as colors]
            [quo2.core :as quo]))

(def mock-data
  [{:name                "Alisher account"
    :balance             "$2,269.12"
    :percentage-value    "16.9%"
    :amount              "$570.24"
    :customization-color :army
   }
   {:name                "Another account"
    :balance             "$1,500.00"
    :percentage-value    "10.5%"
    :amount              "$300.00"
    :customization-color :blue
   }])

(defn cool-preview
  []
  [rn/view
   {:style {:margin-top 200
            :flex       1}}
   [rn/flat-list
    {:data         mock-data
     :keyExtractor hash
     :horizontal   true
     :render-fn    quo/account-card}]])

(defn preview-account-card
  []
  [rn/view
   {:background-color (colors/theme-colors colors/white
                                           colors/neutral-90)
    :flex             1}
   [rn/flat-list
    {:flex                         1
     :keyboard-should-persist-taps :always
     :header                       [cool-preview]
     :key-fn                       str}]])
