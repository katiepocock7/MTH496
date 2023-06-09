# %%
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler 

# %%
def read_dataset(feature_file, label_file):
    ''' Read data set in *.csv to data frame in Pandas'''
    df_X = pd.read_csv(feature_file)
    df_y = pd.read_csv(label_file)
    X = df_X.values # convert values in dataframe to numpy array (features)
    y = df_y.values # convert values in dataframe to numpy array (label)
    return X, y.flatten()

def normalize_features(X_train, X_test):
    scaler = StandardScaler() # call an object function
    scaler.fit(X_train) # calculate mean, std in X_train
    X_train_norm = scaler.transform(X_train) # apply normalization on X_train
    X_test_norm = scaler.transform(X_test) # we use the same normalization on X_test
    return X_train_norm, X_test_norm

class DecisionTreeClassifier():
    def __init__(self, max_depth=5, current_depth=1, max_features=None):        
        self.max_depth = max_depth
        self.current_depth = current_depth
        self.left_tree = None
        self.right_tree = None
        self.max_features = max_features
        
    def fit(self, X, y):
        self.X = X
        self.y = y        
        self.n_features = X.shape[1]
        self.n_samples = X.shape[0]
        if self.current_depth <= self.max_depth:
            self.GINI = self.GINI_calculation(self.y)
            self.best_feature_id, self.best_gain, self.best_split_value = self.find_best_split()
            if self.best_gain > 0:
                self.split_trees()
    
    def split_trees(self):
        # create a left tree
        self.left_tree = DecisionTreeClassifier(max_depth=self.max_depth, current_depth=self.current_depth + 1)
        self.right_tree = DecisionTreeClassifier(max_depth=self.max_depth, current_depth=self.current_depth + 1)
        # partition X according to self.best_split_value and self.best_feature_id
        best_feature_values = self.X[:, self.best_feature_id]
        left_indices = np.where(best_feature_values < self.best_split_value)
        right_indices = np.where(best_feature_values >= self.best_split_value)
        left_tree_X, left_tree_y = self.X[left_indices], self.y[left_indices]
        right_tree_X, right_tree_y = self.X[right_indices], self.y[right_indices]
        # fit left and right tree
        self.left_tree.fit(left_tree_X, left_tree_y)
        self.right_tree.fit(right_tree_X, right_tree_y)    
    
    def find_best_split(self):
        best_feature_id = None
        best_gain = 0
        best_split_value = None
        if self.max_features is None:
            for feature_id in range(self.n_features): # search best_split_value for each feature_id and keep the best one
                current_gain, current_split_value = self.find_best_split_one_feature(feature_id)
                if current_gain is None:
                    continue
                if best_gain < current_gain:
                    best_feature_id = feature_id
                    best_gain = current_gain                
                    best_split_value = current_split_value
        elif self.max_features == 'sqrt':
            rng = np.random.default_rng()
            sampled_features = rng.choice(self.X.shape[1], int(np.sqrt(self.X.shape[1])), replace=False)
            for feature_id in sampled_features: # search best_split_value for each feature_id and keep the best one
                current_gain, current_split_value = self.find_best_split_one_feature(feature_id)
                if current_gain is None:
                    continue
                if best_gain < current_gain:
                    best_feature_id = feature_id
                    best_gain = current_gain                
                    best_split_value = current_split_value    
        return best_feature_id, best_gain, best_split_value
    
    def find_best_split_one_feature(self, feature_id):
        '''
            Return information_gain, split_value
        '''
        feature_values = self.X[:, feature_id]
        unique_feature_values = np.unique(feature_values)
        best_gain = 0.0
        best_split_value = None
        if len(unique_feature_values) == 1:
            return best_gain, best_split_value
        for fea_val in unique_feature_values:
            left_indices, right_indices = np.where(feature_values < fea_val), np.where(feature_values >= fea_val)
            left_tree_X, left_tree_y = self.X[left_indices], self.y[left_indices]
            right_tree_X, right_tree_y = self.X[right_indices], self.y[right_indices]
            left_GINI, right_GINI = self.GINI_calculation(left_tree_y), self.GINI_calculation(right_tree_y)
            left_n_samples, right_n_samples = left_tree_X.shape[0], right_tree_X.shape[0]
            current_gain = self.GINI - (left_n_samples/self.n_samples * left_GINI + right_n_samples/self.n_samples * right_GINI)
            if best_gain < current_gain:
                best_gain = current_gain
                best_split_value = fea_val
        return best_gain, best_split_value                                    
            
    def GINI_calculation(self, y):
        if y.size == 0 or y is None:
            return 0.0
        unique, counts = np.unique(y, return_counts=True)
        prob = counts/y.size # proportions of counts in y
        return 1.0 - np.sum(prob*prob)

    def predict(self, X_test):
        n_test = X_test.shape[0]
        ypred = np.zeros(n_test, dtype=int)  
        for i in range(n_test):
            ypred[i] = self.tree_propogation(X_test[i])            
        return ypred

    def tree_propogation(self, feature):
        if self.is_leaf_node():
            return self.predict_label()
        if feature[self.best_feature_id] < self.best_split_value:
            child_tree = self.left_tree
        else:
            child_tree = self.right_tree
        return child_tree.tree_propogation(feature)

    def predict_label(self):
        unique, counts = np.unique(self.y, return_counts=True)
        return unique[np.argmax(counts)]
    
    def is_leaf_node(self):
        return self.left_tree is None

def accuracy(ypred, yexact):
    p = np.array(ypred == yexact, dtype = int)
    return np.sum(p)/float(len(yexact))





