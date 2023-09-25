from django.http import Http404

class ReviewError(BaseException):
    pass


class NoCurrentReviewError(Http404):
    pass

class ReviewAlreadyStartedError(ReviewError):
    pass

class NoCardsToReviewError(ReviewError):
    pass

class NoMoreCardToReviewError(ReviewError):
    pass

class ReviewCardNotFoundError(ReviewError):
    pass