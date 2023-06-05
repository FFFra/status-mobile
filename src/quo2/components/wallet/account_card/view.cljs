(ns quo2.components.wallet.account-card.view
  (:require [react-native.core :as rn]
            [quo2.foundations.colors :as colors]
            [quo2.components.icon :as icon]
            [quo2.components.wallet.account-card.style :as style]
            [quo2.components.markdown.text :as text]))

(defn view
  [{:keys [name balance percentage-value amount]}]
  [rn/view
   [rn/view style/card
    [rn/view style/profile-container
     [icon/icon :world
      {:color colors/white
       :size  20}]
     [text/text style/account-name
      name]]
    [text/text style/account-value balance]
    [rn/view style/metrics-container
     [rn/view style/percentage-circle
      [icon/icon :positive
       {:color colors/white
        :size  16}]]
     [text/text style/value percentage-value]
     [rn/view style/separator]
     [text/text style/value amount]]]])



