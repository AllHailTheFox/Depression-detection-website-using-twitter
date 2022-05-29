from flask import Flask, flash, render_template, request
import snscrape.modules.twitter as sntwitter
import pandas as pd
import string
import nltk
import numpy as np
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

app= Flask(__name__)
app.config['SECRET_KEY']="my super secret key"

def strip_alphabet(s):
    # counter
    prev_alpha=""
    staging_alpha=""
    final_alpha=""
    # if string more than 2 in length
    if len(s) > 2:
        for i in range(0,len(s)):           
            checking_alpha = s[i]
           # if same as previous alphabet
            if checking_alpha == prev_alpha:          
                try:
                    # check if same as next alphabet
                    next_alpha = s[i+1]
                    if checking_alpha == next_alpha:
                        prev_alpha = checking_alpha
                        staging_alpha += checking_alpha   
                    
                    else:
                        # not the same as next alphabet
                        # append to final_aplha     
                        prev_alpha = checking_alpha
                        staging_alpha += checking_alpha
                        final_alpha += staging_alpha[0:2]
                        # clear off the staging_alpha
                        staging_alpha = ""
                
                except:
                    # this will capture the end of the string as the above will raise error
                    staging_alpha += checking_alpha
                    final_alpha += staging_alpha[0:2]
                    staging_alpha += ""
                    return final_alpha
                    
                
            # not the same as previous alphabet
            else:
                
                # check if same as next alphabet
                try:
                    next_alpha = s[i+1]
                    if checking_alpha == next_alpha:
                         prev_alpha = checking_alpha
                         staging_alpha += checking_alpha 
                    
                    else:
                        # append to final_aplha     
                        prev_alpha = checking_alpha
                        final_alpha += checking_alpha
                        # clear off the staging_alpha
                        staging_alpha = ""                        
                # no next alphabet
                except:
                    final_alpha += checking_alpha
                    staging_alpha = "" 
                    return final_alpha
                                 
    # string less than 2 in length
    else:
        return s



@app.route('/',methods=["GET"], endpoint='main')
def main():
    return render_template('home.html')
    
    
@app.route('/',methods=["POST"],endpoint='Scrape')
def Scrape():
    if request.method == "POST":

        # Creating list to append tweet data to
        tweets_list1 = []
        
        username=request.form.get("input")
        if username == "":
            username="There is no name here"
        else:
            username=request.form.get("input")
        useriddetails='from:'+username

        # Using TwitterSearchScraper to scrape data and append tweets to list
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(useriddetails).get_items()):
            if i>30:
                break
            tweets_list1.append([tweet.date, tweet.id, tweet.content, tweet.user.username])
            
        # Creating a dataframe from the tweets list above 
        tweets_df1 = pd.DataFrame(tweets_list1, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
        

        tweets_df1.to_csv('Original.csv')
        #Check if the dataframe is empty
        if tweets_df1.shape[0] == 0:
            return render_template("home.html",message="No User was found")

        

        tweets_df1['Text'] = tweets_df1["Text"].map(lambda x: x if type(x)!=str else x.lower())


        contraction_dict = {"'cause": ' because', "ain't": ' is not', "aren't": ' are not', "can't": ' cannot', "could've": ' could have', "couldn't": ' could not', "didn't": ' did not', "doesn't": ' does not',
                "don't": ' do not', "hadn't": ' had not', "hasn't": ' has not', "haven't": ' have not', "he'd": ' he would', "he'll": ' he will', "he's": ' he is', "here's": ' here is', "how'd": ' how did', "how'd'y": ' how do you', 
                "how'll": ' how will', "how's": ' how is',"i’d":"i would" ,"i'd": ' i would', "i'd've": ' i would have', "i'll": ' i will', "i'll've": ' i will have', "i'm": ' i am', "i've": ' i have', "isn't": ' is not', "it'd": ' it would', 
                "it'd've": ' it would have', "it'll": ' it will', "it'll've": ' it will have', "it's": ' it is', "let's": ' let us', "ma'am": ' madam', "mayn't": ' may not', "might've": ' might have', "mightn't": ' might not', 
                "mightn't've": ' might not have', "must've": ' must have', "mustn't": ' must not', "mustn't've": ' must not have', "needn't": ' need not', "needn't've": ' need not have', "o'clock": ' of the clock', 
                "oughtn't": ' ought not', "oughtn't've": ' ought not have', "sha'n't": ' shall not', "shan't": ' shall not', "shan't've": ' shall not have', "she'd": ' she would', "she'd've": ' she would have', 
                "she'll": ' she will', "she'll've": ' she will have', "she's": ' she is', "should've": ' should have', "shouldn't": ' should not', "shouldn't've": ' should not have', "so's": ' so as', 
                "so've": ' so have', "that'd": ' that would', "that'd've": ' that would have', "that's": ' that is', "there'd": ' there would', "there'd've": ' there would have', "there's": ' there is', 
                "they'd": ' they would', "they'd've": ' they would have', "they'll": ' they will', "they'll've": ' they will have', "they're": ' they are', "they've": ' they have', "this's": ' this is', 
                "to've": ' to have', "wasn't": ' was not', "we'd": ' we would', "we'd've": ' we would have', "we'll": ' we will', "we'll've": ' we will have', "we're": ' we are', "we've": ' we have', 
                "weren't": ' were not', "what'll": ' what will', "what'll've": ' what will have', "what're": ' what are', "what's": ' what is', "what've": ' what have', "when's": ' when is', "when've": ' when have',
                    "where'd": ' where did', "where's": ' where is', "where've": ' where have', "who'll": ' who will', "who'll've": ' who will have', "who's": ' who is', "who've": ' who have', "why's": ' why is', 
                    "why've": ' why have', "will've": ' will have', "won't": ' will not', "won't've": ' will not have', "would've": ' would have', "wouldn't": ' would not', "wouldn't've": ' would not have', "y'all": ' you all', 
                    "y'all'd": ' you all would', "y'all'd've": ' you all would have', "y'all're": ' you all are', "y'all've": ' you all have', "you'd": ' you would', "you'd've": ' you would have', "you'll": ' you will', 
                    "you'll've": ' you will have', "you're": ' you are', "you've": ' you have'}

        for index, row in tweets_df1.iterrows():
            #Replace words in dictionary
            for key, value in contraction_dict.items():
                tweets_df1['Text'] = tweets_df1['Text'].replace(contraction_dict, regex=True)

            #Remove emoji and https links at the end
            tweets_df1['Text'] = tweets_df1['Text'].str.replace(r'[^\x00-\x7F]+', '', regex=True)
            tweets_df1['Text'] = tweets_df1["Text"].str.replace(r'\s*https?://\S+(\s+|$)', '', regex=True).str.strip()
            tweets_df1['Text'] = tweets_df1['Text'].str.replace('[{}]'.format(string.punctuation), '')
            
            #Strip alphabet that occurs more than 2 times
            tweets_df1["Text"]=tweets_df1["Text"].apply(strip_alphabet)




        tweets_df1.to_csv('Cleaned.csv')
        #Here start classifying
        neg_file = open("negative_words2 rated 4 and 5NEW.txt")
        neg_file_contents = neg_file.read()
        neg_contents_split = neg_file_contents.splitlines()

        pos_file = open("positive_words2withtopwordsNEW.txt")
        pos_file_contents = pos_file.read()
        pos_contents_split = pos_file_contents.splitlines()

        #Break up sentence
        tweets_df1['tokenized_sents'] = tweets_df1.apply(lambda row: nltk.word_tokenize(row['Text']), axis=1)


        #Check if the words is in the positive/negative wordlist and increase the counter and store the words into a new column if it exist.
        for index,row in tweets_df1.iterrows():
            sum=0
            pos_sum=0
            neg_sum=0
            neg_words_exist=""
            pos_word_exist=""

            for value in pos_contents_split:
                if value in row['tokenized_sents']:
                    sum=sum+1
                    pos_sum=pos_sum+1
                    pos_word_exist +=value
                    pos_word_exist +=" "     
            tweets_df1.at[index, 'Pos'] = pos_sum
            tweets_df1.at[index, 'Pos_words_exist']=pos_word_exist

            for value in neg_contents_split:
                if value in row['tokenized_sents']:
                    sum=sum-1
                    neg_sum=neg_sum-1
                    neg_words_exist +=value
                    neg_words_exist +=" " 
            tweets_df1.at[index, 'Neg'] = neg_sum
            tweets_df1.at[index, 'Neg_words_exist']=neg_words_exist
            tweets_df1.at[index,"Final sum"]=sum

            words = tweets_df1['Text'].str.split().map(len)
            tweets_df1['number_of_words'] = words
            tweets_df1['score']=(tweets_df1['Final sum']/tweets_df1['number_of_words'])

            conditions = [
                        (tweets_df1['score'] >= 0.2),
                        (tweets_df1['score'] > 0.2) & (tweets_df1['score'] < -0.5),
                        (tweets_df1['score'] <= -0.5)
                        ]

            values = ['1', '0', '-1']

            tweets_df1['Label'] = np.select(conditions, values)


        tweets_df1.to_csv('Finalized.csv')


        #Generating Graphs
        # For Positive words
        Cloudpos = tweets_df1["Pos_words_exist"]
        Cloudpos.replace('', np.nan, inplace=True)
        Cloudpos.dropna(inplace=True)

        # For Negative words
        Cloudneg = tweets_df1["Neg_words_exist"]
        Cloudneg.replace('', np.nan, inplace=True)
        Cloudneg.dropna(inplace=True)
        

        stopwords = set(STOPWORDS)
        stopwords.update(["Neg_words_exist","Pos_words_exist","float64", "Name", "object", "dtype"])

        
        # Display the generated image:
        if Cloudpos.shape[0] == 0:
            print("")
        else:
            poswordcloud = WordCloud(stopwords=stopwords).generate(str(Cloudpos))
            plt.imshow(poswordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.show()

        if Cloudneg.shape[0] == 0:
            flash('No Depressive words found', 'category1')
        else:
            negwordcloud = WordCloud(stopwords=stopwords).generate(str(Cloudneg))
            plt.imshow(negwordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.show()
        


        timegraph=tweets_df1[['score','Datetime','Pos','Neg','number_of_words']]
        timegraph.rename(columns={'Pos': 'Number of Positive words', 'Neg': 'Number of Negative words','number_of_words':'Total number of words'}, inplace=True)


        for index in timegraph.iterrows():
            timegraph['Datetime'] = timegraph['Datetime'].astype(str).str[:10]
            timegraph['Datetime'] = timegraph['Datetime'].str.replace('T',' ')
            timegraph['Datetime'] = timegraph['Datetime'].str.replace('-','/')
            timegraph = timegraph.loc[timegraph['score']  != 0]
            timegraph['Number of Negative words'] = np.abs(timegraph['Number of Negative words'])

        
        fig, ax = plt.subplots(figsize=(10, 10))

        # Add x-axis and y-axis
        ax.plot(timegraph['Datetime'],
                timegraph['score'],
                color='purple')

        # Set title and labels for axes
        ax.set(xlabel="Date",
            ylabel="Depression Score",
            title="Days that have depression and positivity?")

        plt.axhline(y=0.0, color='r', linestyle='-')
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.show()


        timegraph.plot(x="Datetime", y=["Total number of words", "Number of Positive words","Number of Negative words"], kind="bar")
        plt.xticks(rotation=45)
        plt.show()
 

        finalizedresult='Done'

        return render_template("home.html",message=finalizedresult)
    return render_template('home.html')

@app.route('/Results',methods=["GET"], endpoint='Results')
def Results():
    return render_template('Results.html')


if __name__ == "__main__":
    app.run()





