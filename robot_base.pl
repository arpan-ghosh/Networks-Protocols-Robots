#!/usr/local/bin/perl -w

#
# This program walks through HTML pages, extracting all the links to other
# text/html pages and then walking those links. Basically the robot performs
# a breadth first search through an HTML directory structure.
#
# All other functionality must be implemented
#
# Example:
#
#    robot_base.pl mylogfile.log content.txt http://www.cs.jhu.edu/
#
# Note: you must use a command line argument of http://some.web.address
#       or else the program will fail with error code 404 (document not
#       found).

use strict;

use Carp;
use HTML::LinkExtor;
use HTTP::Request;
use HTTP::Response;
use HTTP::Status;
use LWP::RobotUA;
use URI::URL;

URI::URL::strict( 1 );   # insure that we only traverse well formed URL's

$| = 1;

my $log_file = shift (@ARGV);
my $content_file = shift (@ARGV);
if ((!defined ($log_file)) || (!defined ($content_file))) {
    print STDERR "You must specify a log file, a content file and a base_url\n";
    print STDERR "when running the web robot:\n";
    print STDERR "  ./robot_base.pl mylogfile.log content.txt base_url\n";
    exit (1);
}

open LOG, ">$log_file";
open CONTENT, ">$content_file";

############################################################
##               PLEASE CHANGE THESE DEFAULTS             ##
############################################################

# I don't want to be flamed by web site administrators for
# the lousy behavior of your robots. 

my $ROBOT_NAME = 'jlee562/1.1';
my $ROBOT_MAIL = 'jlee562@cs.jhu.edu';

#
# create an instance of LWP::RobotUA. 
#
# Note: you _must_ include a name and email address during construction 
#       (web site administrators often times want to know who to bitch at 
#       for intrusive bugs).
#
# Note: the LWP::RobotUA delays a set amount of time before contacting a
#       server again. The robot will first contact the base server (www.
#       servername.tag) to retrieve the robots.txt file which tells the
#       robot where it can and can't go. It will then delay. The default 
#       delay is 1 minute (which is what I am using). You can change this 
#       with a call of
#
#         $robot->delay( $ROBOT_DELAY_IN_MINUTES );
#
#       At any rate, if your program seems to be doing nothing, wait for
#       at least 60 seconds (default delay) before concluding that some-
#       thing is wrong.
#

my $robot = new LWP::RobotUA $ROBOT_NAME, $ROBOT_MAIL;
$robot->delay(.01);

my $base_url    = shift(@ARGV);   # the root URL we will start from
$base_url =~ /http:\/\/(www\.)([^\/]*)/;
my $domain = $2;
print "\nDOMAIN: $domain\n";

my @search_urls = ();    # current URL's waiting to be trapsed
my @wanted_urls = ();    # URL's which contain info that we are looking for
my %relevance   = ();    # how relevant is a particular URL to our search
my %pushed      = ();    # URL's which have either been visited or are already
                         #  on the @search_urls array
    
push @search_urls, $base_url;
$pushed{$base_url} = 1;

while (@search_urls) {
    my $url = shift @search_urls;

    my $parsed_url = eval { new URI::URL $url; };

    next if $@;
    next if $parsed_url->scheme !~ /http/i;
	
    #
    # get header information on URL to see it's status (exis-
    # tant, accessible, etc.) and content type. If the status
    # is not okay or the content type is not what we are 
    # looking for skip the URL and move on
    # 

    print LOG "[HEAD ] $url\n";

    my $request  = new HTTP::Request HEAD => $url;
    my $response = $robot->request( $request );
	
    next if $response->code != RC_OK;
    next if ! &wanted_content( $response->content_type, $url);

    print LOG "[GET  ] $url\n";

    $request->method( 'GET' );
    $response = $robot->request( $request );

    next if $response->code != RC_OK;
    next if $response->content_type !~ m@text/html@;
    
    print LOG "[LINKS] $url\n";

    &extract_content ($response->content, $url);

    my @related_urls  = &grab_urls( $response->content, $url);

    foreach my $link (@related_urls) {

	   my $full_url = eval { (new URI::URL $link, $response->base)->abs; };
	    
	   delete $relevance{ $link } and next if $@;

       if (defined $full_url) {
            if ($full_url =~ /$url#.*/){ # Self-referential links
              print "*SR ".$full_url."\n";
                next;
            }

            if ($full_url !~ /\.$domain/){  # Non-local links
               print "*NL ".$full_url."\n";
                next;
            }
        }

       $relevance{ $full_url } = $relevance{ $link };
	   delete $relevance{ $link } if $full_url ne $link;

	   push @search_urls, $full_url and $pushed{ $full_url } = 1
	       if ! exists $pushed{ $full_url };
    }

    #
    # reorder the urls base upon relevance so that we search
    # areas which seem most relevant to us first.
    #
    @search_urls = 
	sort { $relevance{ $b } <=> $relevance{ $a }; } @search_urls;

    #print $url, "\n";
    #for my $i (0 .. scalar @search_urls - 1){
    #    print $i, ": ", $relevance{ $search_urls[$i] }, ": ", $search_urls[$i], "\n"; 
    #}
}

close LOG;
close CONTENT;

exit (0);
    
#
# wanted_content
#
#  this function should check to see if the current URL content
#  is something which is either
#
#    a) something we are looking for (e.g. postscript, pdf,
#       plain text, or html). In this case we should save the URL in the
#       @wanted_urls array.
#
#    b) something we can traverse and search for links
#       (this can be just text/html).
#

sub wanted_content {
    
    my $content = shift;
    my $url = shift;

    # if postcript content, save on wanted_urls array 
    if ($content =~ m@application/postscript@)
    {
        print LOG "[PS   ] $url\n";
        push @wanted_urls, $url; 
    }
    
    if ($content =~ m@application/pdf@)
    {
        print LOG "[PDF  ] $url\n";
        push @wanted_urls, $url;
    }

    return $content =~ m@text/html@;
}

#
# extract_content
#
#  this function should read through the context of all the text/html
#  documents retrieved by the web robot and extract three types of
#  contact information described in the assignment

sub extract_content {
    my $content = shift;
    my $url = shift;

    my $email = ""; 
    my $phone = ""; 
    my $address = ""; 

    skip: 
    while ($content =~ s/<\s*[aA] ([^>]*)>\s*(?:<[^>]*>)*(?:([^<]*)(?:<[^aA>]*>)*<\/\s*[aA]\s*>)?//) {
        # content as long as brackets exist

        my $ref = $1; # inside bracket
        my $text = $2; 

        if( $ref !~ /^\s*body\s+/i){ # if tag is NOT body, next 
            next skip; 
        }

        if ($text =~ /(\w+)@(\w+)\.(\w+)/){ 
            $email = $1 . '/@/' . $2 . '.'. $3;
            print CONTENT "($url; EMAIL; $email)\n";
            print LOG "($url; EMAIL; $email)\n";
        }
        if ($text =~ /(\w+),\s{1}(\w)\s{1}([0-9]{5,})/){
            $address = $1 . ', ' . $2 . ' ' . $3;
            print CONTENT "($url; CITY; $address)\n";
            print LOG "($url; CITY; $address)\n";
        }
        if ($text =~ /([0-9]{3})-([0-9]{3})-([0-9]{4})/){
            $phone = $1 . '-' . $2 . '-' . $3;
            print CONTENT "($url; PHONE; $phone)\n";
            print LOG "($url; PHONE; $phone)\n";
        }

    } # end of while loop 

    return;
}

#
# grab_urls
#
#    PARTIALLY IMPLEMENTED
#
#   this function parses through the content of a passed HTML page and
#   picks out all links and any immediately related text.
#
#   Example:
# 
#     given 
#
#       <a href="somepage.html">This is some web page</a>
#
#     the link "somepage.html" and related text "This is some web page"
#     will be parsed out. However, given
#
#       <a href="anotherpage.html"><img src="image.jpg">
#
#       Further text which does not relate to the link . . .
# 
#     the link "anotherpage.html" will be parse out but the text "Further
#     text which . . . " will be ignored.
#
#   Relevancy based on both the link itself and the related text should
#   be calculated and stored in the %relevance hash
#
#   Example:
#
#      $relevance{ $link } = &your_relevance_method( $link, $text );
#
#   Currently _no_ relevance calculations are made and each link is 
#   given a relevance value of 1.
#

sub grab_urls {
    my $content = shift;
    my $url = shift; # current base url 
    my %urls    = ();    # NOTE: this is an associative array so that we only
                         #       push the same "href" value once.

    skip:
    while ($content =~ s/<\s*[aA] ([^>]*)>\s*(?:<[^>]*>)*(?:([^<]*)(?:<[^aA>]*>)*<\/\s*[aA]\s*>)?//) {
	    
	    my $tag_text = $1;
	    my $reg_text = $2;
	    my $link = "";

	   if (defined $reg_text) {
	       $reg_text =~ s/[\n\r]/ /;
	       $reg_text =~ s/\s{2,}/ /;
	   }

	   if ($tag_text =~ /href\s*=\s*(?:["']([^"']*)["']|([^\s])*)/i) {
	       $link = $1 || $2;

	       $relevance{ $link } = &similarity( $link, $reg_text, $url); 
	       $urls{ $link }      = 1; # or push @urls, $link;
	   }

	   print "text: ", $reg_text, "\n" if defined $reg_text;
	   print "link: ", $link, "\n\n";
    
    } # end of while loop 

    return keys %urls;   # the keys of the associative array hold all the
                         # links we've found (no repeats)
}

# SIMILARITY
#
# PARMA: $link, $text, $url 
#
# Compute simlarity for link and text and return relevancy
# Most relevant to the current url
# 
sub similarity{

    my $link = shift;
    my $text = shift;
    my $url = shift; # current url 

    my @words;
    my $count = () = $link =~ /\//g;
    my $count_base = () = $url =~ /\//g;

    # difference between number of "/" and change to weight
    my $dif = 7 - abs($count - $count_base);

    # grep all the words separated by delimiter 
    if(defined $text){ @words = split / /, $text; }
    my @keys = split /\/|\./, $link; 

    push @words, @keys;
    @words = grep/\S/, @words; 

    # create word hash: words from text and link 
    my %word_hash = ();
    for (keys %word_hash){
        delete $word_hash{$_};
    }

    for my $i(0 .. scalar @words - 1){
        $word_hash{ $words[$i] } += 1; 
    }

    # create urls: words from the orignial link 
    my @urls = split /\/|\./, $url;
    my %url_hash = ();
    for (keys %url_hash){
        delete $url_hash{$_};
    }
    for my $i(0 .. scalar @urls - 1){
        $url_hash{ $urls[$i] } += 1; 
    }

    # calculate the cosine relevance of two vectors
    my $relv = &cosine( \%word_hash, \%url_hash);

    # return the addition of dif and relv 
    return $dif + $relv;
}


# 
# COSINE
# 
# PARMA: vect1, vect2 
#
# Compute vector1 and vector2 cosine similarity 
#
#
sub cosine{

    my $vec1 = shift;
    my $vec2 = shift;

    my $num     = 0;
    my $sum_sq1 = 0;
    my $sum_sq2 = 0;

    my @val1 = values %{ $vec1 };
    my @val2 = values %{ $vec2 };

    # determine shortest length vector. This should speed 
    # things up if one vector is considerable longer than
    # the other (i.e. query vector to document vector).

    if ((scalar @val1) > (scalar @val2)) {
        my $tmp  = $vec1;
        $vec1 = $vec2;
        $vec2 = $tmp;
    }

    # calculate the cross product

    my $key = undef;
    my $val = undef;

    while (($key, $val) = each %{ $vec1 }) {
        $num += $val * ($$vec2{ $key } || 0);
    }

    # calculate the sum of squares

    my $term = undef;

    foreach $term (@val1) { $sum_sq1 += $term * $term; }
    foreach $term (@val2) { $sum_sq2 += $term * $term; }

    return ( $num / sqrt( $sum_sq1 * $sum_sq2 ));
}

