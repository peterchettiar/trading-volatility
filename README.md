# Trading Volatility - Trading Strategies based on the VIX term structure

**Objective**: The aim of this project is to reproduce the trading strategies and their results presented in the research article in a modularized way. Given my interest in volatility trading strategies, specifically those based on the VIX term structure, the research paper titled `Trading strategies based on the VIX term structure` - Link to the research paper [here](./FULLTEXT01.pdf), serves as an excellent foundation for building a library of trading strategies that can ultimately be deployed as a trading algorithm.

### Table of contents

- [1. Introduction](#1-introduction)
  - [VIX Index](#vix-index)
  - [Options and Implied Volatility](#options-and-implied-volatility)
  - [Implied Volatility Calculation Methodology](#implied-volatility-calculation-methodology)
  - [Tradeable Assets](#tradeable-assets)

## 1. Introduction

The thesis of the article aims to answer the following research question:

_How can the term structure dynamics of VIX futures be exploited for abnormal returns?_

> Note: The term structure refers to the different expiration dates of VIX futures contracts. Thus, when we mention "the VIX term structure", we specifically refer to these futures contracts.

Before addressing this question, it is essential to introduce fundamental concepts related to volatility and its instruments. Volatility, or an asset's riskiness, describes fluctuations in its historical prices and is typically represented by standard deviation. In the following sections, we will delve deeper into these concepts. For now, it is crucial to note the inverse relationship between an asset's returns and its volatility, making volatility an interesting choice for hedging an equity portfolio.

The VIX index was created in 1993 to represent the S&P 500's expected future volatility over the next 30 days. This index enables volatility to be traded as an asset through various instruments such as futures, options, and ETFs that utilize this index as their underlying asset.

Before we proceed, let us explore the theoretical background of the VIX index. Understanding how the VIX index was created, along with its unique features and characteristics, is critical, as it serves as the foundation for our volatility trading strategies.

### VIX Index

In this section, we will be looking at some core concepts in relation to derivatives to help us understand more on the mechanics that drive the VIX index. Again the VIX index, similar to the S&P 500 cannot be directly traded. Instead, instruments like ETFs that tracks the index are tradable, examples of which would be introduced in the subsequent sections.

I had mentioned briefly in the previous section what the VIX Index is, the actual definition is as follows:

_"The VIX (CBOE Volatility Index) measures the implied volatility of S&P 500 index options. It is often referred to as the "fear gauge" because it reflects market expectations of future volatility over the next 30 days."_

The key points to note here are the terms `implied volatility` and `index options`.

To understand `implied volatility` we need to have some basic understanding of options, which are popular derivatives products. 

### Options and Implied Volatility

A quick introduction to options that is high-level and by no means definitive but good enough to follow along. For simplicity's sake, we will only look at European options (options that can be only exercised at expiration):
1. Options are derivative products that give the buyer/holder of the option contract the right but not the obligation to exercise the option - there are many kinds of options (e.g. barrier, exotic options) but the most foundational ones are called `call` and `put` options.
2. `call` options give the buyer/holder of the contract to purchase the underlying asset at a specified strike price (usually option is exercised if the strike price is below the current/spot price - this is to say that the option is "in-the-money" and "out-of-the-money" when the strike price is above spot)
3. The buyer/holder of the call option is referred to as `long_call_option` and the counter party who sells/underwrites the contract is called `short_call_option`.
4.  The `put` option gives the buyer/holder of the option the right but not the obligation to sell the underlying asset at a specified strike price (usually option is only exercised if the strike is above the spot price of the underlying asset - you want to be able to sell your asset that you own at a higher rate than the market a.k.a when your option is "in-the-money")
5.  Taking the `long_put_option` as an example, the previous point, the benefit of owning this option is that you're able to sell your asset at a pre-determined price if the spot price is below the strike price and this is limited up to the underlying asset is 0, this is the maximum benefit from the option. On the other hand, if you choose not to exercise the option as the spot is above the strike, then at the expiration of the option you only lose the premium paid for the option.
6.  The counterparty is the `short_put_option`.
7.  "At-the-money" options are where spot price = strike price.

To help understand what has just been discussed, please look at the following payoff profiles for the options:
![image](https://github.com/user-attachments/assets/9ec07388-90a5-47f8-8edc-43d77586de3f)

Now that we have some rudimentary understanding of European options, we can now look at how the prices are derived. This is where the famous Black-Scholes options pricing formula comes into play, the closed-form solution that forms the cornerstone of the entire derivatives market. 

The Black-Scholes options pricing model is as follows:
![image](https://github.com/user-attachments/assets/221d801a-2225-4773-8a15-e29f4133415a)

As you can tell the formula is calculated based on 7 parameters: current time _t_, current stock price _S_, option exercise _T_, strike _K_, interest rate _r_, dividend rate _γ_, and volatility _θ_. Since all parameters but volatility θ are directly observable in the financial markets, the volatility can be estimated by backing the Black-Scholes formula (also referred to as implied volatility), which can be explained as the market expectations of future volatility at a given strike.

Since the implied volatility is derived based on the formula, it should be noted that the formula assumes that the stock prices follow a normal distribution of returns. Also based on the formula you can tell that the implied volatility is a scalar value, as such the implied volatility is the same across the strike dimension.

As such, if you plotted the implied volatility against varying strike prices you would expect to see something flat. However, that is not the case. Instead, you see something more of a "smile" which implies that volatility increases as options contracts are more "out/in-of-the-money". The following image summarises this effect in the practical world. This was the case as traders realized that extreme events should be factored into options pricing.
![image](https://github.com/user-attachments/assets/d1c7116d-a758-4b09-b858-8364a2930bb9)

In fact, near-term equity options and forex options lean more toward aligning with a volatility smile, whereas index options and long-term equity options tend to align more with a volatility skew/smirk. This is because OTM put options tend to be priced higher and hence higher implied volatility.

### Implied Volatility Calculation Methodology

Because the Black-Scholes formula doesn't allow for direct algebraic solving for volatility, numerical methods like Newton-Raphson or bisection method are used to estimate implied volatility. The general steps are:
1. Start with a general guess for volatility (e.g. historical volatility)
2. Plug this volatility into the Black-Scholes formula to calculate a theoretical option price
3. Compare the theoretical price with the actual market price of the option.
4. Adjust the volatility initial guess until the theoretical price converges to the actual market price (within a small margin of error).

### VIX Index Derivation

Now that we have a solid foundation of the concepts involved

### Tradeable Assets

In the research article, their sample period is October 11th, 2011 to March 31st, 2020. The datasets for the derivatives consist of 2134 data points each, a number representing the number of days included. The following are the assets they used in their research:

_Data Sources:_

| ETF/Index Name | Ticker Symbol | Price Data Used |
|:---------------|:--------------|:----------------|
| VIX Index | VIX | Opening only |
| VIX Futures (1-month) | VX | Opening only |
| Proshares VIX Short-Term Futures ETF | VIXY | Both (Opening & Closing) |
| Proshares Short VIX Short-Term Futures ETF | SVXY | Both (Opening & Closing) |
| SPDR S&P 500 ETF Trust | SPY | Both (Opening & Closing) |
