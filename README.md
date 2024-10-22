# Trading Volatility - Trading Strategies based on the VIX term structure

**Objective** : The aim of this project is to reproduce the trading strategies and their results presented in the research article in a modularized way. Given my interest in volatility trading strategies, specifically those based on the VIX term structure, the research paper titled `Trading strategies based on the VIX term structure` - Link to research paper [here](./FULLTEXT01.pdf), serves as an excellent foundation for building a library of trading strategies that can ultimately be deployed as a trading algorithm.

### Table of contents

- [1. Introduction](#1-introduction)
  - [VIX Index](#vix-index)

## 1. Introduction

The thesis of the article, aims to answer the following research question:

_How can the term structure dynamics of VIX futures be exploited for abnormal returns?_

> Note: The term structure refers to the different expiration dates of VIX futures contracts. Thus, when we mention the VIX term structure, we are specifically referring to these futures contracts.

Before addressing this question, it is essential to introduce fundamental concepts related to volatility instruments. Volatility, or the riskiness of an asset, describes the fluctuations in its historical prices and is typically represented by standard deviation. In the following sections, we will delve deeper into these concepts. For now, it is crucial to note the inverse relationship between an asset's returns and its volatility, making volatility an interesting choice for hedging an equity portfolio.

The VIX index was created in 1993 to represent the S&P 500's expected future volatility over the next 30 days. This index enables volatility to be traded as an asset through various instruments such as futures, options, and ETFs that utilize this index as their underlying asset.

Before we proceed, let us explore the theoretical background of the VIX index. Understanding how the VIX index was created, along with its unique features and characteristics, is critical, as it serves as the foundation for our volatility trading strategies.

### VIX Index

