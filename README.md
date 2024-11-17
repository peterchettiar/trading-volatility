# Trading Volatility - Trading Strategies based on the VIX term structure

**Objective**: The aim of this project is to reproduce the trading strategies and their results presented in the research article in a modularized way. Given my interest in volatility trading strategies, specifically those based on the VIX term structure, the research paper titled `Trading strategies based on the VIX term structure` - Link to the research paper [here](./FULLTEXT01.pdf), serves as an excellent foundation for building a library of trading strategies that can ultimately be deployed as a trading algorithm.

### Table of contents

- [1. Introduction](#1-introduction)
  - [VIX Index](#vix-index)
  - [Options and Implied Volatility](#options-and-implied-volatility)
  - [Implied Volatility Calculation Methodology](#implied-volatility-calculation-methodology)
  - [VIX Index Derivation](#vix-index-derivation)
  - [Tradeable Assets](#tradeable-assets)
- [2. Trading Strategies](#2-trading-strategies)
  - [Long short VIX (LSV)](#long-short-vix-lsv)

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

Now that we have a solid foundation of the concepts involving options, we can proceed with the the VIX Index calculation. Please find the following VIX formula:

![image](https://github.com/user-attachments/assets/894e3ccc-6c18-4911-a072-0b1f13d25de0)

A high-level summary of how to use this formula is as follows:

_The CBOE VIX is calculated using the weighted prices of SPX at-the-money and out-of-the-money options with expiration dates between 23 days and 37 days in the future. As a result, there are two sets of options in the calculation. After interpolating the variance of these two sets of options, transforming it into a standard deviation, and multiplying everything by 100, you get the VIX Index value._

But keep in mind that it is overly simplified, and recreating the index via code is no easy feat; hence, I would not be attempting to do so either. Instead, there is a really good article that I came across that explains step-by-step how to calculate VIX [here](https://financestu.com/vix-formula/#The_Initial_VIX_Formula).

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

> Note: If you really need to, please do your own research on the individual assets listed in the table above. It will not be gone through in this README file.

**Disclaimer**: The two ETFs that are to be used in our trading strategies are meant to give us long and short exposure to VIX Futures. This should not be traded individually as a "buy-and-hold" strategy. This is because the underlying assets in the ETF are actual futures contracts that are being rolled over everytime the contract expires, hence the negative roll-yield effect if term structure of the VIX Futures in contango. Therefore, it would be advised to understand more on `VIXY` and `SVXY`, and realise that these are assets that need to be actively managed as well as to be intended for short-term use.

## 2. Trading Strategies

Now that we have a working knowledge of the various concepts associated with the VIX index as well as its derivation, we can now move on to the crux of the research article; _The Trading Strategies_.

There are three strategies tried and tested in this paper:
1. Long short VIX (LSV)
2. Hedged long short VIX (HLSV)
3. Long SPY Long VIX (LSLV)

The above strategies, which will be defined in detail in due course, are based on the thesis of the research article that was mentioned above in the introduction section. A couple of points regarding the development of the strategies:
1. VIX futures index, just like the S&P 500 index, cannot be traded directly but via ETFs that replicate the movement of the index - As such the trading strategies will employ the use of the ETFs mentioned in Data Sources.
2. However such ETFs are not suitable for "buy-and-hold" investments because of the negative roll yield - since the VIX futures term structure is normally in contango (with the rare exception of backwardation in times of increased volatility and risk), this refers to the longer-dated maturity being more expensive than the shorter-term futures and the spot price. Hence, whenever we roll over the contracts in a "buy-and-hold" strategy in a contango market, we cause the position to generate a negative return over time.
3. Therefore, the trading strategies were designed in such a way as to reduce the negative effects of the contango trap.
4. For exposure to long VIX positions we use the VIXY ETF, and for short VIX positions, the SVXY ETF. For exposure to the S&P 500 long and short positions, the SPY ETF will be used.
5. Every trade assumes fees (brokerage: 0.15%, slippage: 0.04%, and management fee: 0.85% annually).

## Long short VIX (LSV)

Steps to determine the positions that need to be entered into / exited:
1. Start by calculating the Basis for the day ([VIX futures opening price / VIX spot opening price] - 1) - this is an indicator for  buy and sell signals when the VIX term structure is either in contango or backwardation (basis < 0, VIX term structure in backwardation, and contango if basis > 0).
2. If the basis for the day signals backwardation (i.e. near-term maturities are priced higher than longer-dated maturities):
   - LSV enters a long position in VIXY at the market open, but if there is already an open position the trader can proceed to the next day without any execution.
   - But before opening any long VIXY position, we need to check for any open long SVXY - if there is, close it before purchasing a long VIXY.
3. If the basis is in contango at the beginning of the trading day:
   - a long SVXY position is entered at the market open, unless a long SVXY position is already open. In that case, trader can proceed to next day.
   - Again before going long on the SVXY position (if you don't already have an open position), check if you have any long position in VIXY, close before going long on SVXY 

The summary of the LSV Strategy is as follows:

![image](https://github.com/user-attachments/assets/1609080b-7035-4dcc-9850-2fdb69be0b5f)
