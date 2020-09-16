from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    title = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.title 


class Ingredient(models.Model):
    title = models.CharField(max_length=100)
    dimension = models.CharField(max_length=100)

    def __str__(self):
        return (self.title + self.dimension)


class Amount(models.Model):
    quantity = models.IntegerField(default=1)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='amount')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='amount')

    def __str__(self):
        return str(self.quantity)


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe')
    image = models.ImageField(upload_to='recipe/')
    description = models.TextField(max_length=5000)
    ingredients = models.ManyToManyField(Ingredient, through='Amount', through_fields=('recipe', 'ingredient'))
    tags = models.ManyToManyField(Tag)
    duration = models.IntegerField(default=1)
    pub_date = models.DateTimeField('date_published', auto_now_add=True, db_index=True)
    
    def __str__(self):
        return self.title

class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name= 'favorite_recipes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_user')
    pub_date = models.DateTimeField('date_published', auto_now_add=True, db_index=True,)
    

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_users')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cart_recipes')
